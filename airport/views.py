from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Q, Prefetch

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
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)
from airport.filters import CityFilter, AirportFilter, RouteFilter, FlightFilter
from base.permissions import (
    IsAdminOrIsAuthenticatedReadOnly,
    IsAdminAllowDeleteOrIsAuthenticatedReadAndCreateOnly,
)


class AirplaneTypeViewSet(ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["name"]


class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "airplane_type__name"]
    ordering_fields = ["capacity"]

    def get_queryset(self):
        return Airplane.objects.annotate(
            capacity=F("rows") * F("seats_in_row")
        ).select_related("airplane_type")

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return AirplaneSerializer
        return AirplaneDetailSerializer


class CountryViewSet(ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]


class CityViewSet(ModelViewSet):
    queryset = City.objects.select_related("country")
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "country__name"]
    ordering_fields = ["name", "country__name"]
    filterset_class = CityFilter

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return CitySerializer
        return CityDetailSerializer


class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.select_related("closest_big_city__country")
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "name",
        "closest_big_city__name",
        "closest_big_city__country__name",
    ]
    ordering_fields = ["name", "closest_big_city__name"]
    filterset_class = AirportFilter

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportDetailSerializer
        return AirportSerializer


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.select_related(
        "source__closest_big_city__country", "destination__closest_big_city__country"
    )
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "source__name",
        "source__closest_big_city__name",
        "source__closest_big_city__country__name",
        "destination__name",
        "destination__closest_big_city__name",
        "destination__closest_big_city__country__name",
    ]
    ordering_fields = [
        "source__name",
        "source__closest_big_city__name",
        "source__closest_big_city__country__name",
        "destination__name",
        "destination__closest_big_city__name",
        "destination__closest_big_city__country__name",
        "distance",
    ]
    filterset_class = RouteFilter

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class CrewMemberViewSet(ModelViewSet):
    queryset = CrewMember.objects.all()
    serializer_class = CrewMemberSerializer
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["first_name", "last_name"]


class FlightViewSet(ModelViewSet):
    permission_classes = [IsAdminOrIsAuthenticatedReadOnly]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [
        "route__source__name",
        "route__source__closest_big_city__name",
        "route__source__closest_big_city__country__name",
        "route__destinaton__name",
        "route__destination__closest_big_city__name",
        "route__destination__closest_big_city__country__name",
        "airplane__name",
        "airplane__airplane__type__name",
    ]
    ordering_fields = ["departure_time", "arrival_time"]
    filterset_class = FlightFilter

    def get_queryset(self):
        return Flight.objects.select_related(
            "route__source__closest_big_city__country",
            "route__destination__closest_big_city__country",
            "airplane__airplane_type",
        ).prefetch_related(
            Prefetch(
                "flight_crew", queryset=FlightCrew.objects.select_related("crew_member")
            ),
            "tickets",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAdminAllowDeleteOrIsAuthenticatedReadAndCreateOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            Prefetch(
                "tickets",
                queryset=Ticket.objects.select_related("flight").prefetch_related(
                    Prefetch(
                        "flight__route",
                        queryset=Route.objects.select_related(
                            "source__closest_big_city__country",
                            "destination__closest_big_city__country",
                        ),
                    ),
                    "flight__airplane__airplane_type",
                    Prefetch(
                        "flight__flight_crew",
                        queryset=FlightCrew.objects.select_related("crew_member"),
                    ),
                ),
            )
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer
