from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    # airport
    path("api/airport/", include("airport.urls", namespace="airport")),
    # accounts
    path("api/accounts/", include("accounts.urls", namespace="accounts")),
    # docs
    path("api/doc/", SpectacularAPIView.as_view(), name="schema"),
    path("api/doc/swagger/", SpectacularSwaggerView.as_view(), name="swagger"),
    path("api/doc/redoc/", SpectacularRedocView.as_view(), name="redoc"),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
