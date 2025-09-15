from django.db import models
from django.conf import settings
from timezone_field import TimeZoneField


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class CrewMember(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities"
    )
    is_capital = models.BooleanField(default=False)
    timezone = TimeZoneField(use_pytz=False)

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="airports"
    )

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.source_id} -> {self.destination_id}: {self.distance}(km)"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    crew_members = models.ManyToManyField(
        CrewMember, related_name="flights", through="FlightCrew"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"Flight: {self.departure_time} -> {self.arrival_time}"


class FlightCrew(models.Model):
    class CrewRole(models.TextChoices):
        CAPTAIN = "CAPTAIN", "Captain (Pilot in Command)"
        FIRST_OFFICER = "FIRST_OFFICER", "First Officer (Co-Pilot)"
        FLIGHT_ATTENDANT = "FLIGHT_ATTENDANT", "Flight Attendant"
        PURSER = "PURSER", "Purser"
        DISPATCHER = "DISPATCHER", "Dispatcher"

    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="flight_crew"
    )
    crew_member = models.ForeignKey(
        CrewMember, on_delete=models.CASCADE, related_name="flight_crew"
    )
    role = models.CharField(max_length=20, choices=CrewRole.choices)

    class Meta:
        verbose_name_plural = "flight crew"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    tickets = models.ManyToManyField(Ticket, related_name="orders")
