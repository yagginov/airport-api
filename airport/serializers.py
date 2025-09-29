from rest_framework import serializers
from django.db import transaction

from base.serializer_fields import TimeZoneSerializerChoicesField
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
    capacity = serializers.IntegerField(read_only=True)

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
    timezone = TimeZoneSerializerChoicesField(use_pytz=False)

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


class FlightCrewListSerializer(FlightCrewSerializer):
    crew_member = serializers.SlugRelatedField(slug_field="full_name", read_only=True)


class FlightCrewDetailSerializer(FlightCrewSerializer):
    crew_member = CrewMemberSerializer(read_only=True)


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
        with transaction.atomic():
            flight_crew_data = validated_data.pop("flight_crew", [])
            flight = Flight.objects.create(**validated_data)

            for flight_crew in flight_crew_data:
                FlightCrew.objects.create(flight=flight, **flight_crew)

        return flight

    def update(self, instance: Flight, validated_data: dict) -> Flight:
        with transaction.atomic():
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
    flight_crew = FlightCrewListSerializer(many=True, read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        flight = attrs.get("flight")
        row = attrs.get("row")
        seat = attrs.get("seat")
        errors = {}
        if flight:
            airplane = flight.airplane
            if row and row > airplane.rows:
                errors["row"] = (
                    f"Row {row} exceeds airplane's max rows ({airplane.rows})"
                )
            if seat and seat > airplane.seats_in_row:
                errors["seat"] = (
                    f"Seat {seat} exceeds airplane's max seats in row ({airplane.seats_in_row})"
                )
            if Ticket.objects.filter(row=row, seat=seat, flight=flight).exists():
                errors["non_field_errors"] = [
                    "Duplicate ticket for this flight (row, seat)"
                ]
        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)


class TicketFlightSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat"]
        read_only_fields = ["id"]


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(read_only=True)
    airplane = AirplaneDetailSerializer(read_only=True)
    tickets = TicketFlightSerializer(many=True, read_only=True)
    flight_crew = FlightCrewDetailSerializer(many=True, read_only=True)

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

    def validate_tickets(self, value):
        seen = set()
        for t in value:
            key = (
                t["row"],
                t["seat"],
                t["flight"].id if hasattr(t["flight"], "id") else t["flight"],
            )
            if key in seen:
                raise serializers.ValidationError(
                    "Duplicate tickets in request: (row, seat, flight) must be unique."
                )
            seen.add(key)
        return value

    def create(self, validated_data: dict) -> Order:
        with transaction.atomic():
            tickets = validated_data.pop("tickets", [])
            order = Order.objects.create(user=self._user, **validated_data)

            for ticket in tickets:
                Ticket.objects.create(order=order, **ticket)

        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True)
