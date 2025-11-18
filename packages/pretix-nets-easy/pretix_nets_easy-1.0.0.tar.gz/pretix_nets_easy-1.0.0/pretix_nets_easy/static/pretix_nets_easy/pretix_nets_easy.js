/*global $, gettext, Dibs */
'use strict';

$(function () {
    // https://developers.nets.eu/nets-easy/en-EU/api/#localization
    const supportedLanguages = {
        'en': 'en-GB',
        'da': 'da-DK',
        'nl': 'nl-NL',
        'fi': 'fi-FI',
        'fr': 'fr-FR',
        'de': 'de-DE',
        'nb': 'nb-NO',
        'pl': 'pl-PL',
        'es': 'es-ES',
        'sk': 'sk-SK',
        'sv': 'sv-SE',
    };

    const checkoutOptions = {
        checkoutKey: $.trim($("#nets_easy_checkout_key").html()),
        paymentId: $.trim($("#nets_easy_pid").html()),
        containerId: "paymentcontainer",
        language: supportedLanguages[$.trim($("body").attr("data-locale"))] || 'en-GB',
    };
    const checkout = new Dibs.Checkout(checkoutOptions);
    checkout.on('payment-completed', function (response) {
        waitingDialog.show(gettext("Processing payment…"));
        $("#paymentcontainer form").get(0).submit();
    });
});