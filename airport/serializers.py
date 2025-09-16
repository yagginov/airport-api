from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from airport.models import (
    AirplaneType,
    Airplane,
    Country,
    City,
    Airport,
    Route,
    CrewMember,
    Flight,
    FlightCrew,
    Ticket,
    Order,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]
        read_only_fields = ["id"]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type", "capacity"]
        read_only_fields = ["id", "capacity"]


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]
        read_only_fields = ["id"]


class CitySerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(use_pytz=False)

    class Meta:
        model = City
        fields = ["id", "name", "country", "is_capital", "timezone"]
        read_only_fields = ["id"]


class CityDetailSerializer(CitySerializer):
    country = CountrySerializer(read_only=True)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city"]
        read_only_fields = ["id"]


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(slug_field="name", read_only=True)
    country = serializers.SlugRelatedField(
        slug_field="name", read_only=True, source="closest_big_city.country"
    )

    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city", "country"]
        read_only_fields = ["id", "closest_big_city", "country"]


class AirportDetailSerializer(AirportSerializer):
    closest_big_city = CityDetailSerializer(read_only=True)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]
        read_only_fields = ["id"]


class RouteListSerializer(RouteSerializer):
    source = AirportListSerializer(read_only=True)
    destination = AirportListSerializer(read_only=True)


class RouteDetailSerializer(RouteSerializer):
    source = AirportDetailSerializer(read_only=True)
    destination = AirportDetailSerializer(read_only=True)


class CrewMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewMember
        fields = ["id", "first_name", "last_name", "full_name"]
        read_only_fields = ["id", "full_name"]


class FlightCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightCrew
        fields = ["crew_member", "role"]


class FlightSerializer(serializers.ModelSerializer):
    flight_crew = FlightCrewSerializer(many=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "flight_crew",
            "departure_time",
            "arrival_time",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data: dict) -> Flight:
        flight_crew_data = validated_data.pop("flight_crew", [])
        flight = Flight.objects.create(**validated_data)

        for flight_crew in flight_crew_data:
            FlightCrew.objects.create(flight=flight, **flight_crew)

        return flight

    def update(self, instance: Flight, validated_data: dict) -> Flight:
        crew_member_data = validated_data.pop("flight_crew", [])

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        for crew_member in crew_member_data:
            _, _ = FlightCrew.objects.get_or_create(flight=instance, **crew_member)
        return instance


class FlightListSerializer(FlightSerializer):
    route = RouteListSerializer(read_only=True)
    airplane = serializers.SlugRelatedField(slug_field="name", read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]
        read_only_fields = ["id"]


class TicketFlightSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat"]
        read_only_fields = ["id"]


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(read_only=True)
    airplane = AirplaneDetailSerializer(read_only=True)
    tickets = TicketFlightSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "flight_crew",
            "departure_time",
            "arrival_time",
            "tickets",
        ]
        read_only_fields = ["id", "route", "airplane", "tickets"]


class FlightTicketSerializer(FlightDetailSerializer):
    tickets = None

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "flight_crew",
            "departure_time",
            "arrival_time",
        ]
        read_only_fields = ["id", "route", "airplane"]


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)


class TicketDetailSerializer(TicketSerializer):
    flight = FlightTicketSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]
        read_only_fields = ["id"]

    @property
    def _user(self):
        request = self.context.get("request")
        if request:
            return request.user

    def create(self, validated_data: dict) -> Order:
        tickets = validated_data.pop("tickets", [])
        order = Order.objects.create(user=self._user, **validated_data)

        for ticket in tickets:
            Ticket.objects.create(order=order, **ticket)

        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True)
