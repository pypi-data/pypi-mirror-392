from django.utils.translation import gettext_lazy

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = "pretix_nets_easy"
    verbose_name = "Nexi Nets Checkout"

    class PretixPluginMeta:
        name = gettext_lazy("Nexi Nets Checkout")
        author = "pretix Team"
        description = gettext_lazy(
            "Accept payments through the Nexi Nets Checkout (formerly DIBS Easy payment gateway)"
        )
        picture = "pretix_nets_easy/logo.svg"
        visible = True
        version = __version__
        category = "PAYMENT"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA
