from rest_framework.viewsets import ModelViewSet

from airport.models import (
    AirplaneType,
    Airplane,
    CrewMember,
    Country,
    City,
    Airport,
    Route,
    Flight,
    FlightCrew,
    Ticket,
    Order,
)
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneDetailSerializer,
    CountrySerializer,
    CitySerializer,
    CityDetailSerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportDetailSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    CrewMemberSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
)


class AirplaneTypeViewSet(ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return AirplaneSerializer
        return AirplaneDetailSerializer


class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(ModelViewSet):
    queryset = City.objects.select_related("country")

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return CitySerializer
        return CityDetailSerializer


class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.select_related("closest_big_city__country")

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportDetailSerializer
        return AirportSerializer


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.select_related("source__closest_big_city__country", "destination__closest_big_city__country")

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class CrewMemberViewSet(ModelViewSet):
    queryset = CrewMember.objects.all()
    serializer_class = CrewMemberSerializer


class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer
