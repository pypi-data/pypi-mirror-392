import hashlib
import json
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from functools import cached_property
from pretix.base.models import Order, OrderPayment
from pretix.base.payment import PaymentException
from pretix.multidomain.urlreverse import eventreverse


class NetsEasyOrderView:
    def dispatch(self, request, *args, **kwargs):
        try:
            self.order = request.event.orders.get(code=kwargs["order"])
            if (
                hashlib.sha1(self.order.secret.lower().encode()).hexdigest()
                != kwargs["hash"].lower()
            ):
                raise Http404("Unknown order")
        except Order.DoesNotExist:
            # Do a hash comparison as well to harden timing attacks
            if (
                "abcdefghijklmnopq".lower()
                == hashlib.sha1("abcdefghijklmnopq".encode()).hexdigest()
            ):
                raise Http404("Unknown order")
            else:
                raise Http404("Unknown order")
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def pprov(self):
        return self.payment.payment_provider

    @property
    def payment(self):
        return get_object_or_404(
            self.order.payments,
            pk=self.kwargs["payment"],
            provider="nets_easy",
        )

    def _redirect_to_order(self):
        return redirect(
            eventreverse(
                self.request.event,
                "presale:event.order",
                kwargs={"order": self.order.code, "secret": self.order.secret},
            )
            + ("?paid=yes" if self.order.status == Order.STATUS_PAID else "")
        )


@method_decorator(xframe_options_exempt, "dispatch")
class PayView(NetsEasyOrderView, TemplateView):
    template_name = ""

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data()

        if self.payment.state not in [
            OrderPayment.PAYMENT_STATE_CREATED,
            OrderPayment.PAYMENT_STATE_PENDING,
        ]:
            return self._redirect_to_order()
        elif not ctx["pid"]:
            messages.error(
                self.request,
                _(
                    "Sorry, there was an error in the payment process. Please try again."
                ),
            )
            return self._redirect_to_order()
        else:
            r = render(request, "pretix_nets_easy/pay.html", ctx)
            return r

    def post(self, request, *args, **kwargs):
        res = self.pprov._get_payment(self.payment)
        summary = res["payment"]["summary"]

        if "chargedAmount" in summary and summary[
            "chargedAmount"
        ] == self.pprov._get_amount(self.payment):
            return self._redirect_to_order()
        elif "reservedAmount" in summary and summary[
            "reservedAmount"
        ] == self.pprov._get_amount(self.payment):
            try:
                self.pprov._charge_payment(self.payment)
                self.order.refresh_from_db()
            except PaymentException as e:
                messages.error(self.request, str(e))
            return self._redirect_to_order()
        else:
            messages.error(
                self.request,
                _(
                    "Sorry, there was an error in the payment process. Please try again."
                ),
            )
            return self._redirect_to_order()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["checkouturl"] = (
            "https://{}checkout.dibspayment.eu/v1/checkout.js?v=1".format(
                "test." if self.request.event.testmode else ""
            )
        )
        ctx["order"] = self.order
        ctx["payment"] = self.payment
        ctx["pid"] = (
            self.payment.info_data["payment"]["paymentId"]
            if "payment" in self.payment.info_data
            else self.payment.info_data["paymentId"]
        )
        ctx["checkout_key"] = self.request.event.settings.get(
            "payment_nets_easy_{}_checkout_key".format(
                "test" if self.request.event.testmode else "live"
            ),
            None,
        )
        ctx["payment_hash"] = hashlib.sha1(
            self.payment.order.secret.lower().encode()
        ).hexdigest()
        return ctx

    def dispatch(self, request, *args, **kwargs):
        self.request.pci_dss_payment_page = True
        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_exempt, "dispatch")
class NotifyView(NetsEasyOrderView, TemplateView):
    template_name = ""

    def post(self, request, *args, **kwargs):
        self.pprov._get_payment(self.payment)
        self.payment.refresh_from_db()
        self.order.refresh_from_db()

        webhook_events = [
            "payment.created",
            "payment.reservation.created.v2",
            "payment.checkout.completed",
            "payment.charge.created.v2",
            "payment.charge.failed",
            # The following events are valid events, but we don't need them delivered async.
            # 'payment.refund.initiated.v2', 'payment.refund.failed', 'payment.refund.completed',
            # 'payment.cancel.created', 'payment.cancel.failed'
        ]

        body = json.loads(request.body.decode("utf-8") or "{}")

        if body.get("event", None) in webhook_events:
            self.order.log_action(
                "pretix_nets_easy.event",
                data={
                    "local_id": self.payment.local_id,
                    "provider": self.payment.provider,
                    "data": body,
                },
            )

            if self.payment.state not in (
                OrderPayment.PAYMENT_STATE_PENDING,
                OrderPayment.PAYMENT_STATE_CONFIRMED,
            ):
                summary = self.payment.info_data["payment"]["summary"]

                # The customer has completed the checkout and we can charge them now
                if body.get("event") in ["payment.checkout.completed"]:
                    if "reservedAmount" in summary and summary[
                        "reservedAmount"
                    ] == self.pprov._get_amount(self.payment):
                        try:
                            self.pprov._charge_payment(self.payment)
                        except PaymentException:
                            pass

                # The customers charge has been processed successfully
                elif body.get("event") in ["payment.charge.created.v2"]:
                    if "chargedAmount" in summary and summary[
                        "chargedAmount"
                    ] == self.pprov._get_amount(self.payment):
                        self.payment.confirm()

                # The customers charge has failed for some reason
                elif body.get("event") in ["payment.charge.failed"]:
                    self.payment.fail()

        return HttpResponse(status=200)
