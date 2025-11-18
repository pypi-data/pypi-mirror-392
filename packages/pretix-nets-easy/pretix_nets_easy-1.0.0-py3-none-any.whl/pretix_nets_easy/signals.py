from django.dispatch import receiver
from django.http import HttpRequest, HttpResponse
from django.urls import resolve
from django.utils.translation import gettext_lazy as _, gettext_noop  # NoQA
from i18nfield.strings import LazyI18nString
from pretix.base.middleware import _merge_csp, _parse_csp, _render_csp
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import logentry_display, register_payment_providers
from pretix.presale.signals import process_response

from .payment import NetsEasy


@receiver(register_payment_providers, dispatch_uid="payment_nets_easy")
def register_payment_provider(sender, **kwargs):
    from .payment import NetsEasy

    return [NetsEasy]


@receiver(signal=logentry_display, dispatch_uid="payment_nets_easy_logentry_display")
def logentry_display(sender, logentry, **kwargs):
    if not logentry.action_type.startswith("pretix_nets_easy.event"):
        return

    d = logentry.parsed_data.get("data", {})
    t = d.get("event") or "?"
    return _("Nets Easy reported an event: {}.".format(t))


@receiver(signal=process_response, dispatch_uid="payment_nets_easy_process_response")
def signal_process_response(
    sender, request: HttpRequest, response: HttpResponse, **kwargs
):
    provider = NetsEasy(sender)
    url = resolve(request.path_info)

    if provider.settings.get("_enabled", as_type=bool) and "pay" in url.url_name:
        if "Content-Security-Policy" in response:
            h = _parse_csp(response["Content-Security-Policy"])
        else:
            h = {}

        csps = {
            "script-src": [
                "https://{}checkout.dibspayment.eu/".format(
                    "test." if sender.testmode else ""
                )
            ],
            "style-src": [
                "https://{}checkout.dibspayment.eu/".format(
                    "test." if sender.testmode else ""
                )
            ],
            "connect-src": [
                "https://{}checkout.dibspayment.eu/".format(
                    "test." if sender.testmode else ""
                )
            ],
            "frame-src": [
                "https://{}checkout.dibspayment.eu/".format(
                    "test." if sender.testmode else ""
                )
            ],
        }

        _merge_csp(h, csps)

        if h:
            response["Content-Security-Policy"] = _render_csp(h)
    return response


settings_hierarkey.add_default(
    "payment_nets_easy_public_name",
    LazyI18nString.from_gettext(gettext_noop("Credit Card, Invoice, Digital Wallets")),
    LazyI18nString,
)
