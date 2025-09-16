import django_filters as filters

from airport.models import Country, City, Airport, Route, Flight, Order, Ticket


class CityFilter(filters.FilterSet):
    class Meta:
        model = City
        fields = ["country"]


class AirportFilter(filters.FilterSet):
    city = filters.ModelChoiceFilter(
        label="City", field_name="closest_big_city", queryset=City.objects.all()
    )
    country = filters.ModelChoiceFilter(
        label="Country",
        field_name="closest_big_city__country",
        queryset=Country.objects.all(),
    )

    class Meta:
        model = Airport
        fields = ["city", "country"]


class RouteFilter(filters.FilterSet):
    source_city = filters.ModelChoiceFilter(
        label="Source city",
        field_name="source__closest_big_city",
        queryset=City.objects.all(),
    )
    destination_city = filters.ModelChoiceFilter(
        label="Destination city",
        field_name="destination__closest_big_city",
        queryset=City.objects.all(),
    )
    source_airport = filters.ModelChoiceFilter(
        label="Source airport", field_name="source", queryset=Airport.objects.all()
    )
    destination_airport = filters.ModelChoiceFilter(
        label="Destination airport",
        field_name="destination",
        queryset=Airport.objects.all(),
    )
    source_country = filters.ModelChoiceFilter(
        label="Source country",
        field_name="source__closest_big_city__country",
        queryset=Country.objects.all(),
    )
    destination_country = filters.ModelChoiceFilter(
        label="Destination country",
        field_name="destination__closest_big_city__country",
        queryset=Country.objects.all(),
    )

    class Meta:
        model = Route
        fields = [
            "source_city",
            "destination_city",
            "source_airport",
            "destination_airport",
            "source_country",
            "destination_country",
        ]


class FlightFilter(filters.FilterSet):
    departure_time = filters.DateFilter(field_name="departure_time", lookup_expr="date")
    arrival_time = filters.DateFilter(field_name="arrival_time", lookup_expr="date")
    source_city = filters.ModelChoiceFilter(
        label="Source city",
        field_name="route__source__closest_big_city",
        queryset=City.objects.all(),
    )
    destination_city = filters.ModelChoiceFilter(
        label="Destination city",
        field_name="route__destination__closest_big_city",
        queryset=City.objects.all(),
    )
    source_airport = filters.ModelChoiceFilter(
        label="Source airport",
        field_name="route__source",
        queryset=Airport.objects.all(),
    )
    destination_airport = filters.ModelChoiceFilter(
        label="Destination airport",
        field_name="route__destination",
        queryset=Airport.objects.all(),
    )
    source_country = filters.ModelChoiceFilter(
        label="Source country",
        field_name="route__source__closest_big_city__country",
        queryset=Country.objects.all(),
    )
    destination_country = filters.ModelChoiceFilter(
        label="Destination country",
        field_name="route__destination__closest_big_city__country",
        queryset=Country.objects.all(),
    )

    class Meta:
        model = Flight
        fields = [
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "source_city",
            "source_airport",
            "source_country",
            "destination_city",
            "destination_airport",
            "destination_country",
        ]
