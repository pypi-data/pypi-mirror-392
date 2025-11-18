import hashlib
import json
import logging
import requests
from collections import OrderedDict
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.forms import URLField
from django.http import HttpRequest
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from i18nfield.forms import I18nFormField, I18nTextInput
from i18nfield.strings import LazyI18nString
from json import JSONDecodeError
from pretix.base.decimal import round_decimal
from pretix.base.forms import SecretKeySettingsField
from pretix.base.models import Order, OrderPayment, OrderRefund
from pretix.base.payment import BasePaymentProvider, PaymentException
from pretix.helpers import OF_SELF
from pretix.multidomain.urlreverse import build_absolute_uri, eventreverse
from requests import HTTPError

from . import __version__
from .forms import NetsEasyKeyValidator

logger = logging.getLogger(__name__)


class NetsEasy(BasePaymentProvider):
    identifier = "nets_easy"
    verbose_name = _("Nexi Nets Checkout")
    client = None
    endpoint = None

    @property
    def settings_form_fields(self):
        d = OrderedDict(
            [
                (
                    "public_name",
                    I18nFormField(
                        label=_("Payment method name"),
                        widget=I18nTextInput,
                        help_text=_(
                            "Since pretix cannot deduce the available payment methods on the hosted Payment Page, it "
                            "cannot display a choice of allowed payment methods to the customer. You will need to name "
                            "choice of this payment method to your liking. You could for example provide a list of all "
                            'allowed payment methods like "Credit Card, Invoice".'
                        ),
                    ),
                ),
                (
                    "terms_url",
                    URLField(
                        label=_("Terms & Conditions URL"),
                        help_text=_(
                            "Link to your shops terms and conditions, as required by your payment processor."
                        ),
                    ),
                ),
                (
                    "test_secret_key",
                    SecretKeySettingsField(
                        label=_("Test Secret Key"),
                        required=False,
                        validators=(NetsEasyKeyValidator("test-secret-key-"),),
                    ),
                ),
                (
                    "test_checkout_key",
                    SecretKeySettingsField(
                        label=_("Test Checkout Key"),
                        required=False,
                        validators=(NetsEasyKeyValidator("test-checkout-key-"),),
                    ),
                ),
                (
                    "live_secret_key",
                    SecretKeySettingsField(
                        label=_("Live Secret Key"),
                        required=False,
                        validators=(NetsEasyKeyValidator("live-secret-key-"),),
                    ),
                ),
                (
                    "live_checkout_key",
                    SecretKeySettingsField(
                        label=_("Live Checkout Key"),
                        required=False,
                        validators=(NetsEasyKeyValidator("live-checkout-key-"),),
                    ),
                ),
            ]
            + list(super().settings_form_fields.items())
        )

        d.move_to_end("_enabled", last=False)
        return d

    def _init_api(self, testmode):
        if not self.client:
            s = requests.Session()
            s.headers = {
                "Authorization": (
                    self.settings.test_secret_key
                    if testmode
                    else self.settings.live_secret_key
                ),
                "CommercePlatformTag": "pretix-nets-easy/{}".format(__version__),
            }

            self.client = s
            self.endpoint = "https://{}api.dibspayment.eu".format(
                "test." if testmode else ""
            )

    @property
    def public_name(self):
        return str(
            self.settings.get("public_name", as_type=LazyI18nString)
            or _("Credit Card, Invoice, Digital Wallets")
        )

    @property
    def test_mode_message(self):
        if self.settings.test_secret_key and self.settings.test_checkout_key:
            return mark_safe(
                _(
                    "The Nexi Nets Checkout plugin is operating in test mode. You can use one of <a {cardargs}>many test "
                    "cards</a> or <a {invoiceargs}>invoice test addresses</a> to perform a transaction. No money will "
                    "actually be transferred."
                ).format(
                    cardargs='href="https://developer.nexigroup.com/nexi-checkout/en-EU/docs/test-card-processing/#build-sample-credit-cards" '
                    'target="_blank"',
                    invoiceargs='href="https://developer.nexigroup.com/nexi-checkout/en-EU/docs/'
                    'test-invoice-installment-processing/#build-sample-invoice-nordic-addresses" '
                    'target="_blank"',
                )
            )
        return None

    def payment_refund_supported(self, payment: OrderPayment) -> bool:
        return True

    def payment_partial_refund_supported(self, payment: OrderPayment) -> bool:
        return True

    def is_allowed(self, request: HttpRequest, total: Decimal = None) -> bool:
        global_allowed = super().is_allowed(request, total)

        if request.event.testmode:
            local_allowed = (
                self.settings.test_secret_key and self.settings.test_checkout_key
            )
        else:
            local_allowed = (
                self.settings.live_secret_key and self.settings.live_checkout_key
            )

        return global_allowed and local_allowed

    def payment_is_valid_session(self, request: HttpRequest):
        return True

    def payment_form_render(self, request, total):
        template = get_template("pretix_nets_easy/checkout_payment_form.html")
        ctx = {"request": request}
        return template.render(ctx)

    def checkout_confirm_render(self, request, order: Order = None):
        template = get_template("pretix_nets_easy/checkout_payment_confirm.html")
        ctx = {
            "request": request,
            "event": self.event,
            "settings": self.settings,
            "provider": self,
        }
        return template.render(ctx)

    def execute_payment(self, request: HttpRequest, payment: OrderPayment):
        self._create_payment(request, payment)

        return eventreverse(
            self.event,
            "plugins:pretix_nets_easy:pay",
            kwargs={
                "order": payment.order.code,
                "payment": payment.pk,
                "hash": hashlib.sha1(payment.order.secret.lower().encode()).hexdigest(),
            },
        )

    def execute_refund(self, refund: OrderRefund):
        self._refund_payment(refund)

    def payment_control_render(self, request: HttpRequest, payment: OrderPayment):
        template = get_template("pretix_nets_easy/control.html")
        ctx = {
            "payment_info": payment.info_data,
        }
        return template.render(ctx)

    def refund_control_render(self, request: HttpRequest, refund: OrderRefund):
        template = get_template("pretix_nets_easy/control.html")
        ctx = {
            "payment_info": refund.info_data,
        }
        return template.render(ctx)

    def _amount_to_decimal(self, cents):
        places = settings.CURRENCY_PLACES.get(self.event.currency, 2)
        return round_decimal(float(cents) / (10**places), self.event.currency)

    def _decimal_to_int(self, amount):
        places = settings.CURRENCY_PLACES.get(self.event.currency, 2)
        return int(amount * 10**places)

    def _get_amount(self, payment):
        return self._decimal_to_int(payment.amount)

    def _create_payment(self, request: HttpRequest, payment: OrderPayment):
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
        payload = {
            "order": {
                "items": [
                    {
                        "reference": payment.full_id,
                        "name": payment.full_id,
                        "quantity": 1,
                        "unit": "x",
                        "unitPrice": self._get_amount(payment),
                        "grossTotalAmount": self._get_amount(payment),
                        "netTotalAmount": self._get_amount(payment),
                    }
                ],
                "amount": self._get_amount(payment),
                "currency": payment.order.event.currency,
                "reference": "Order {}".format(payment.order.full_code),
            },
            "checkout": {
                "url": build_absolute_uri(
                    request.event,
                    "plugins:pretix_nets_easy:pay",
                    kwargs={
                        "order": payment.order.code,
                        "payment": payment.pk,
                        "hash": hashlib.sha1(
                            payment.order.secret.lower().encode()
                        ).hexdigest(),
                    },
                ),
                "integrationType": "EmbeddedCheckout",
                "consumer": {},
                "termsUrl": self.settings.terms_url,
                "consumerType": {"supportedTypes": ["B2C", "B2B"]},
                "charge": False,
                "publicDevice": True,
                "merchantHandlesConsumerData": True,
                "appearance": {
                    "displayOptions": {
                        "showMerchantName": False,
                        "showOrderSummary": False,
                    },
                    "textOptions": {"completePaymentButtonText": "pay"},
                },
            },
            "notifications": {
                "webhooks": [
                    {
                        "eventName": eventname,
                        "url": build_absolute_uri(
                            request.event,
                            "plugins:pretix_nets_easy:notify",
                            kwargs={
                                "order": payment.order.code,
                                "payment": payment.pk,
                                "hash": hashlib.sha1(
                                    payment.order.secret.lower().encode()
                                ).hexdigest(),
                            },
                        ),
                        # We actually don't care about the authorization since we only take incoming notifications
                        # as a trigger to lookup the transaction using verified sources.
                        "authorization": "wedontcarebutyouforceustoputsomethinghere",
                    }
                    for eventname in webhook_events
                ]
            },
        }

        try:
            self._init_api(request.event.testmode)
            req = self.client.post("{}/v1/payments".format(self.endpoint), json=payload)
            req.raise_for_status()
        except HTTPError:
            try:
                d = req.json()
            except JSONDecodeError:
                d = {"error": True, "detail": req.text}
            payment.fail(info=d)
            logger.exception("nets Easy error: %s" % req.text)
            raise PaymentException(
                _(
                    "We had trouble communicating with the payment service. Please try again and get "
                    "in touch with us if this problem persists."
                )
            )
        else:
            data = req.json()
            payment.info = json.dumps(data)
            payment.state = OrderPayment.PAYMENT_STATE_CREATED
            payment.save(update_fields=["info", "state"])

            # We get the payment again, just so we have the most possible data available to us in the info_data.
            self._get_payment(payment)

        return data["paymentId"]

    def _get_payment(self, payment: OrderPayment):
        payment_id = (
            payment.info_data["payment"]["paymentId"]
            if "payment" in payment.info_data
            else payment.info_data["paymentId"]
        )

        try:
            self._init_api(payment.order.event.testmode)
            req = self.client.get("{}/v1/payments/{}".format(self.endpoint, payment_id))
            req.raise_for_status()
        except HTTPError:
            try:
                d = req.json()
            except JSONDecodeError:
                d = {"error": True, "detail": req.text}

            payment.fail(info=d)
            logger.exception("nets Easy error: %s" % req.text)
            raise PaymentException(
                _(
                    "We had trouble communicating with the payment service. Please try again and get "
                    "in touch with us if this problem persists."
                )
            )
        else:
            data = req.json()
            payment.info = json.dumps(data)
            payment.save(update_fields=["info"])

        return data

    def _charge_payment(self, payment: OrderPayment):
        with transaction.atomic():
            OrderPayment.objects.select_for_update(of=OF_SELF).get(pk=payment.pk)

            payment_id = (
                payment.info_data["payment"]["paymentId"]
                if "payment" in payment.info_data
                else payment.info_data["paymentId"]
            )

            payload = {
                "amount": self._get_amount(payment),
            }

            try:
                self._init_api(payment.order.event.testmode)
                req = self.client.post(
                    "{}/v1/payments/{}/charges".format(self.endpoint, payment_id),
                    json=payload,
                )
                req.raise_for_status()
            except HTTPError:
                logger.exception("nets Easy error: %s" % req.text)
                raise PaymentException(
                    _(
                        "We had trouble communicating with the payment service. Please try again and get "
                        "in touch with us if this problem persists."
                    )
                )
            else:
                data = req.json()
                if "chargeId" in data:
                    payment.confirm()

                    # We get the payment again, just so we have the most possible data available to us in the info_data.
                    self._get_payment(payment)

    def _refund_payment(self, refund: OrderRefund):
        # Partial refunds need to also update pass which items are being refunded. Since we only pass a single big
        # "meta-item", we have to monkeypatch it to reflect the refunded amount.
        payload = {
            "amount": self._get_amount(refund),
            "orderItems": [
                refund.payment.info_data["payment"]["charges"][0]["orderItems"][0]
            ],
        }
        payload["orderItems"][0]["unitPrice"] = self._get_amount(refund)
        payload["orderItems"][0]["grossTotalAmount"] = self._get_amount(refund)
        payload["orderItems"][0]["netTotalAmount"] = self._get_amount(refund)

        try:
            self._init_api(refund.order.event.testmode)
            req = self.client.post(
                "{}/v1/charges/{}/refunds".format(
                    self.endpoint,
                    refund.payment.info_data["payment"]["charges"][0]["chargeId"],
                ),
                json=payload,
            )
            req.raise_for_status()
        except HTTPError:
            logger.exception("nets Easy error: %s" % req.text)
            raise PaymentException(
                _(
                    "We had trouble communicating with the payment service. Please try again and get "
                    "in touch with us if this problem persists."
                )
            )
        else:
            data = req.json()
            if "refundId" in data:
                refund.done()
                refund.info = json.dumps(data)
                refund.save()

                # We get the payment again, just so we have the most possible data available to us in the info_data.
                self._get_payment(refund.payment)
