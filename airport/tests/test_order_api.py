from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from airport.models import (
    Order,
    Ticket,
    Flight,
    Country,
    City,
    Airport,
    Route,
    AirplaneType,
    Airplane,
)
from django.utils import timezone


User = get_user_model()


class TestOrderApi(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="admin", password="p", is_staff=True
        )
        cls.user = User.objects.create_user(username="user", password="p")
        cls.country = Country.objects.create(name="Ukraine")
        cls.city = City.objects.create(
            name="Kyiv", country=cls.country, is_capital=True, timezone="Europe/Kiev"
        )
        cls.airport = Airport.objects.create(name="Boryspil", closest_big_city=cls.city)
        cls.route = Route.objects.create(
            source=cls.airport, destination=cls.airport, distance=0
        )
        cls.type1 = AirplaneType.objects.create(name="Boeing 737")
        cls.airplane = Airplane.objects.create(
            name="Boeing 737-800", rows=30, seats_in_row=6, airplane_type=cls.type1
        )
        cls.flight = Flight.objects.create(
            route=cls.route,
            airplane=cls.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2),
        )
        cls.order = Order.objects.create(user=cls.user)
        cls.ticket = Ticket.objects.create(
            row=1, seat=1, flight=cls.flight, order=cls.order
        )

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def test_list_orders_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:order-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_orders_user(self):
        self.authenticate(self.user)
        url = reverse("airport:order-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order.id)

    def test_list_orders_anon(self):
        url = reverse("airport:order-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_order_user(self):
        self.authenticate(self.user)
        url = reverse("airport:order-detail", args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order.id)

    def test_retrieve_order_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:order-detail", args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_order_anon(self):
        url = reverse("airport:order-detail", args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_user(self):
        self.authenticate(self.user)
        url = reverse("airport:order-list")
        data = {"tickets": [{"row": 2, "seat": 2, "flight": self.flight.id}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(id=response.data["id"]).exists())

    def test_create_order_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:order-list")
        data = {"tickets": [{"row": 3, "seat": 3, "flight": self.flight.id}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(id=response.data["id"]).exists())

    def test_create_order_anon(self):
        url = reverse("airport:order-list")
        data = {"tickets": [{"row": 4, "seat": 4, "flight": self.flight.id}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_user(self):
        self.authenticate(self.user)
        url = reverse("airport:order-detail", args=[self.order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:order-detail", args=[self.order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_anon(self):
        url = reverse("airport:order-detail", args=[self.order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ordering_order(self):
        self.authenticate(self.user)
        url = reverse("airport:order-list")
        response = self.client.get(url, {"ordering": "created_at"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_order_with_invalid_row(self):
        self.authenticate(self.user)
        url = reverse("airport:order-list")
        data = {"tickets": [{"row": 31, "seat": 1, "flight": self.flight.id}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("row", str(response.data))

    def test_create_order_with_invalid_seat(self):
        self.authenticate(self.user)
        url = reverse("airport:order-list")
        data = {"tickets": [{"row": 1, "seat": 7, "flight": self.flight.id}]}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("seat", str(response.data))

    def test_create_order_with_duplicate_ticket(self):
        self.authenticate(self.user)
        url = reverse("airport:order-list")
        data = {
            "tickets": [
                {"row": 2, "seat": 2, "flight": self.flight.id},
                {"row": 2, "seat": 2, "flight": self.flight.id},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duplicate", str(response.data).lower())
