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
    Order
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
