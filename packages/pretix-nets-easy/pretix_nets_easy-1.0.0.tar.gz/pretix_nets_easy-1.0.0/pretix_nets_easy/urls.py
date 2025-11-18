from django.urls import include, path

from .views import NotifyView, PayView

event_patterns = [
    path(
        "nets_easy/",
        include(
            [
                path(
                    "<str:order>/<str:hash>/<int:payment>/",
                    PayView.as_view(),
                    name="pay",
                ),
                path(
                    "notify/<str:order>/<str:hash>/<str:payment>/",
                    NotifyView.as_view(),
                    name="notify",
                ),
            ]
        ),
    ),
]
