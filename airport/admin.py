from django.contrib import admin

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


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ["name", "rows", "seats_in_row", "capacity"]


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "full_name"]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "is_capital", "timezone"]


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ["name", "closest_big_city"]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ["source", "destination", "distance"]


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ["route", "airplane", "departure_time", "arrival_time"]


@admin.register(FlightCrew)
class FlightCrewAdmin(admin.ModelAdmin):
    list_display = ["flight", "crew_member", "role"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["row", "seat", "flight"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user"]
