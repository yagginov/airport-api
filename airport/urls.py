from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
)

router = DefaultRouter()
router.register("airplane_types", AirplaneTypeViewSet, basename="airplane-type")
router.register("airplanes", AirplaneViewSet, basename="aplane")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "ariport"
