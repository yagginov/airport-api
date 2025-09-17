from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from airport.models import Country, City, Airport, Route, AirplaneType, Airplane, CrewMember, Flight, FlightCrew

User = get_user_model()

class TestFlightApi(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username="admin", password="p", is_staff=True)
        cls.user = User.objects.create_user(username="user", password="p")
        cls.country = Country.objects.create(name="Ukraine")
        cls.city1 = City.objects.create(name="Kyiv", country=cls.country, is_capital=True, timezone="Europe/Kiev")
        cls.city2 = City.objects.create(name="Lviv", country=cls.country, is_capital=False, timezone="Europe/Kiev")
        cls.airport1 = Airport.objects.create(name="Boryspil", closest_big_city=cls.city1)
        cls.airport2 = Airport.objects.create(name="Lviv Airport", closest_big_city=cls.city2)
        cls.route = Route.objects.create(source=cls.airport1, destination=cls.airport2, distance=500)
        cls.type1 = AirplaneType.objects.create(name="Boeing 737")
        cls.airplane = Airplane.objects.create(name="Boeing 737-800", rows=30, seats_in_row=6, airplane_type=cls.type1)
        cls.crew1 = CrewMember.objects.create(first_name="Ivan", last_name="Ivanov")
        cls.crew2 = CrewMember.objects.create(first_name="Anna", last_name="Shevchenko")
        cls.flight = Flight.objects.create(
            route=cls.route,
            airplane=cls.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2)
        )
        FlightCrew.objects.create(flight=cls.flight, crew_member=cls.crew1, role=FlightCrew.CrewRole.CAPTAIN)
        FlightCrew.objects.create(flight=cls.flight, crew_member=cls.crew2, role=FlightCrew.CrewRole.FIRST_OFFICER)

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def test_list_flights_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_flights_user(self):
        self.authenticate(self.user)
        url = reverse("airport:flight-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_flights_anon(self):
        url = reverse("airport:flight-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_flight_admin(self):
        self.authenticate(self.admin)
        obj = self.flight
        url = reverse("airport:flight-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], obj.id)

    def test_retrieve_flight_user(self):
        self.authenticate(self.user)
        obj = self.flight
        url = reverse("airport:flight-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], obj.id)

    def test_retrieve_flight_anon(self):
        obj = self.flight
        url = reverse("airport:flight-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_flight_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() + timezone.timedelta(hours=2)).isoformat(),
            "flight_crew": [
                {"crew_member": self.crew1.id, "role": FlightCrew.CrewRole.CAPTAIN},
                {"crew_member": self.crew2.id, "role": FlightCrew.CrewRole.FIRST_OFFICER},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_flight_user(self):
        self.authenticate(self.user)
        url = reverse("airport:flight-list")
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() + timezone.timedelta(hours=2)).isoformat(),
            "flight_crew": [
                {"crew_member": self.crew1.id, "role": FlightCrew.CrewRole.CAPTAIN},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_flight_anon(self):
        url = reverse("airport:flight-list")
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() + timezone.timedelta(hours=2)).isoformat(),
            "flight_crew": [
                {"crew_member": self.crew1.id, "role": FlightCrew.CrewRole.CAPTAIN},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_flight_admin(self):
        self.authenticate(self.admin)
        obj = self.flight
        url = reverse("airport:flight-detail", args=[obj.id])
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() + timezone.timedelta(hours=3)).isoformat(),
            "flight_crew": [
                {"crew_member": self.crew1.id, "role": FlightCrew.CrewRole.CAPTAIN},
                {"crew_member": self.crew2.id, "role": FlightCrew.CrewRole.FIRST_OFFICER},
            ]
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_flight_user(self):
        self.authenticate(self.user)
        obj = self.flight
        url = reverse("airport:flight-detail", args=[obj.id])
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() + timezone.timedelta(hours=4)).isoformat(),
            "flight_crew": [
                {"crew_member": self.crew1.id, "role": FlightCrew.CrewRole.CAPTAIN},
            ]
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_flight_anon(self):
        obj = self.flight
        url = reverse("airport:flight-detail", args=[obj.id])
        data = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now().isoformat(),
            "arrival_time": (timezone.now() + timezone.timedelta(hours=5)).isoformat(),
            "flight_crew": [
                {"crew_member": self.crew1.id, "role": FlightCrew.CrewRole.CAPTAIN},
            ]
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_flight_admin(self):
        self.authenticate(self.admin)
        obj = self.flight
        url = reverse("airport:flight-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_flight_user(self):
        self.authenticate(self.user)
        obj = self.flight
        url = reverse("airport:flight-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_flight_anon(self):
        obj = self.flight
        url = reverse("airport:flight-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_flight(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        response = self.client.get(url, {"search": "Boryspil"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        found = any(f["id"] == self.flight.id for f in response.data)
        self.assertTrue(found)

    def test_ordering_flight(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        response = self.client.get(url, {"ordering": "departure_time"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_source_city(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        response = self.client.get(url, {"source_city": self.city1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [f for f in Flight.objects.all() if f.route.source.closest_big_city_id == self.city1.id]
        self.assertGreaterEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(f["id"] == obj.id for f in response.data)
            self.assertTrue(found)

    def test_filter_destination_city(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        response = self.client.get(url, {"destination_city": self.city2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [f for f in Flight.objects.all() if f.route.destination.closest_big_city_id == self.city2.id]
        self.assertGreaterEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(f["id"] == obj.id for f in response.data)
            self.assertTrue(found)

    def test_filter_source_airport(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        response = self.client.get(url, {"source_airport": self.airport1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [f for f in Flight.objects.all() if f.route.source_id == self.airport1.id]
        self.assertGreaterEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(f["id"] == obj.id for f in response.data)
            self.assertTrue(found)

    def test_filter_destination_airport(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        response = self.client.get(url, {"destination_airport": self.airport2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [f for f in Flight.objects.all() if f.route.destination_id == self.airport2.id]
        self.assertGreaterEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(f["id"] == obj.id for f in response.data)
            self.assertTrue(found)

    def test_filter_source_country(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        response = self.client.get(url, {"source_country": self.country.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [f for f in Flight.objects.all() if f.route.source.closest_big_city.country_id == self.country.id]
        self.assertGreaterEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(f["id"] == obj.id for f in response.data)
            self.assertTrue(found)

    def test_filter_destination_country(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        response = self.client.get(url, {"destination_country": self.country.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [f for f in Flight.objects.all() if f.route.destination.closest_big_city.country_id == self.country.id]
        self.assertGreaterEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(f["id"] == obj.id for f in response.data)
            self.assertTrue(found)

    def test_filter_departure_time(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        date = self.flight.departure_time.date().isoformat()
        response = self.client.get(url, {"departure_time": date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [f for f in Flight.objects.all() if f.departure_time.date().isoformat() == date]
        self.assertGreaterEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(f["id"] == obj.id for f in response.data)
            self.assertTrue(found)

    def test_filter_arrival_time(self):
        self.authenticate(self.admin)
        url = reverse("airport:flight-list")
        date = self.flight.arrival_time.date().isoformat()
        response = self.client.get(url, {"arrival_time": date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [f for f in Flight.objects.all() if f.arrival_time.date().isoformat() == date]
        self.assertGreaterEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(f["id"] == obj.id for f in response.data)
            self.assertTrue(found)
