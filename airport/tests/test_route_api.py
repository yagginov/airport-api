from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from airport.models import Country, City, Airport, Route

User = get_user_model()


class TestRouteApi(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="admin", password="p", is_staff=True
        )
        cls.user = User.objects.create_user(username="user", password="p")
        cls.country = Country.objects.create(name="Ukraine")
        cls.city1 = City.objects.create(
            name="Kyiv", country=cls.country, is_capital=True, timezone="Europe/Kiev"
        )
        cls.city2 = City.objects.create(
            name="Lviv", country=cls.country, is_capital=False, timezone="Europe/Kiev"
        )
        cls.airport1 = Airport.objects.create(
            name="Boryspil", closest_big_city=cls.city1
        )
        cls.airport2 = Airport.objects.create(
            name="Lviv Airport", closest_big_city=cls.city2
        )
        cls.routes = [
            Route.objects.create(
                source=cls.airport1, destination=cls.airport2, distance=500
            ),
            Route.objects.create(
                source=cls.airport2, destination=cls.airport1, distance=500
            ),
        ]

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def test_list_routes_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_routes_user(self):
        self.authenticate(self.user)
        url = reverse("airport:route-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_routes_anon(self):
        url = reverse("airport:route-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_route_admin(self):
        self.authenticate(self.admin)
        obj = self.routes[0]
        url = reverse("airport:route-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], obj.id)

    def test_retrieve_route_user(self):
        self.authenticate(self.user)
        obj = self.routes[1]
        url = reverse("airport:route-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], obj.id)

    def test_retrieve_route_anon(self):
        obj = self.routes[0]
        url = reverse("airport:route-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_route_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        data = {
            "source": self.airport1.id,
            "destination": self.airport2.id,
            "distance": 600,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_route_user(self):
        self.authenticate(self.user)
        url = reverse("airport:route-list")
        data = {
            "source": self.airport2.id,
            "destination": self.airport1.id,
            "distance": 700,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_route_anon(self):
        url = reverse("airport:route-list")
        data = {
            "source": self.airport1.id,
            "destination": self.airport2.id,
            "distance": 800,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_route_admin(self):
        self.authenticate(self.admin)
        obj = self.routes[0]
        url = reverse("airport:route-detail", args=[obj.id])
        data = {
            "source": self.airport1.id,
            "destination": self.airport2.id,
            "distance": 999,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj.refresh_from_db()
        self.assertEqual(obj.distance, 999)

    def test_update_route_user(self):
        self.authenticate(self.user)
        obj = self.routes[1]
        url = reverse("airport:route-detail", args=[obj.id])
        data = {
            "source": self.airport2.id,
            "destination": self.airport1.id,
            "distance": 888,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        obj.refresh_from_db()
        self.assertNotEqual(obj.distance, 888)

    def test_update_route_anon(self):
        obj = self.routes[0]
        url = reverse("airport:route-detail", args=[obj.id])
        data = {
            "source": self.airport1.id,
            "destination": self.airport2.id,
            "distance": 777,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        obj.refresh_from_db()
        self.assertNotEqual(obj.distance, 777)

    def test_delete_route_admin(self):
        self.authenticate(self.admin)
        obj = self.routes[1]
        url = reverse("airport:route-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_route_user(self):
        self.authenticate(self.user)
        obj = self.routes[0]
        url = reverse("airport:route-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_route_anon(self):
        obj = self.routes[1]
        url = reverse("airport:route-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_route(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        response = self.client.get(url, {"search": "Boryspil"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [
            t
            for t in self.routes
            if "Boryspil" in t.source.name or "Boryspil" in t.destination.name
        ]
        self.assertGreaterEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(r["id"] == obj.id for r in response.data)
            self.assertTrue(found)

    def test_ordering_route(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        response = self.client.get(url, {"ordering": "distance"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sorted_by_distance = sorted(self.routes, key=lambda x: x.distance)
        response_ids = [t["id"] for t in response.data]
        expected_ids = [t.id for t in sorted_by_distance]
        self.assertEqual(response_ids, expected_ids)

    def test_filter_source_city(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        response = self.client.get(url, {"source_city": self.city1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [
            r for r in self.routes if r.source.closest_big_city_id == self.city1.id
        ]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(r["id"] == obj.id for r in response.data)
            self.assertTrue(found)

    def test_filter_destination_city(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        response = self.client.get(url, {"destination_city": self.city2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [
            r for r in self.routes if r.destination.closest_big_city_id == self.city2.id
        ]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(r["id"] == obj.id for r in response.data)
            self.assertTrue(found)

    def test_filter_source_airport(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        response = self.client.get(url, {"source_airport": self.airport1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [r for r in self.routes if r.source_id == self.airport1.id]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(r["id"] == obj.id for r in response.data)
            self.assertTrue(found)

    def test_filter_destination_airport(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        response = self.client.get(url, {"destination_airport": self.airport2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [r for r in self.routes if r.destination_id == self.airport2.id]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(r["id"] == obj.id for r in response.data)
            self.assertTrue(found)

    def test_filter_source_country(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        response = self.client.get(url, {"source_country": self.country.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [
            r
            for r in self.routes
            if r.source.closest_big_city.country_id == self.country.id
        ]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(r["id"] == obj.id for r in response.data)
            self.assertTrue(found)

    def test_filter_destination_country(self):
        self.authenticate(self.admin)
        url = reverse("airport:route-list")
        response = self.client.get(url, {"destination_country": self.country.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [
            r
            for r in self.routes
            if r.destination.closest_big_city.country_id == self.country.id
        ]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(r["id"] == obj.id for r in response.data)
            self.assertTrue(found)
