from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CountryViewSet,
    CityViewSet,
)

router = DefaultRouter()

router.register("airplane_types", AirplaneTypeViewSet, basename="airplane-type")
router.register("airplanes", AirplaneViewSet, basename="aplane")
router.register("countries", CountryViewSet, basename="country")
router.register("cities", CityViewSet, basename="city")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "ariport"
