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
    Order
)
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneDetailSerializer,
)


class AirplaneTypeViewSet(ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")

    def get_serializer_class(self):
        if self.action in ("create", "update"):
            return AirplaneSerializer
        return AirplaneDetailSerializer
