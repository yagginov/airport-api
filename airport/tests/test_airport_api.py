from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from airport.models import Airport, City, Country

User = get_user_model()


class TestAirportApi(APITestCase):
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
        cls.airports = [
            Airport.objects.create(name="Boryspil", closest_big_city=cls.city1),
            Airport.objects.create(name="Zhuliany", closest_big_city=cls.city1),
            Airport.objects.create(name="Lviv Airport", closest_big_city=cls.city2),
        ]

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def test_list_airports_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:airport-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        names = sorted([t["name"] for t in response.data])
        expected = sorted([t.name for t in self.airports])
        self.assertEqual(names, expected)

    def test_list_airports_user(self):
        self.authenticate(self.user)
        url = reverse("airport:airport-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_airports_anon(self):
        url = reverse("airport:airport-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_airport_admin(self):
        self.authenticate(self.admin)
        obj = self.airports[0]
        url = reverse("airport:airport-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_airport_user(self):
        self.authenticate(self.user)
        obj = self.airports[1]
        url = reverse("airport:airport-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_airport_anon(self):
        obj = self.airports[2]
        url = reverse("airport:airport-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_airport_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:airport-list")
        data = {"name": "Odessa Airport", "closest_big_city": self.city1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Airport.objects.filter(name="Odessa Airport").exists())

    def test_create_airport_user(self):
        self.authenticate(self.user)
        url = reverse("airport:airport-list")
        data = {"name": "Kharkiv Airport", "closest_big_city": self.city2.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Airport.objects.filter(name="Kharkiv Airport").exists())

    def test_create_airport_anon(self):
        url = reverse("airport:airport-list")
        data = {"name": "Dnipro Airport", "closest_big_city": self.city1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Airport.objects.filter(name="Dnipro Airport").exists())

    def test_update_airport_admin(self):
        self.authenticate(self.admin)
        obj = self.airports[0]
        url = reverse("airport:airport-detail", args=[obj.id])
        data = {"name": "Boryspil Updated", "closest_big_city": self.city1.id}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj.refresh_from_db()
        self.assertEqual(obj.name, "Boryspil Updated")

    def test_update_airport_user(self):
        self.authenticate(self.user)
        obj = self.airports[1]
        url = reverse("airport:airport-detail", args=[obj.id])
        data = {"name": "Zhuliany Updated", "closest_big_city": self.city1.id}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Zhuliany Updated")

    def test_update_airport_anon(self):
        obj = self.airports[2]
        url = reverse("airport:airport-detail", args=[obj.id])
        data = {"name": "Lviv Airport Updated", "closest_big_city": self.city2.id}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Lviv Airport Updated")

    def test_delete_airport_admin(self):
        self.authenticate(self.admin)
        obj = self.airports[2]
        url = reverse("airport:airport-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Airport.objects.filter(id=obj.id).exists())

    def test_delete_airport_user(self):
        self.authenticate(self.user)
        obj = self.airports[1]
        url = reverse("airport:airport-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Airport.objects.filter(id=obj.id).exists())

    def test_delete_airport_anon(self):
        obj = self.airports[0]
        url = reverse("airport:airport-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Airport.objects.filter(id=obj.id).exists())

    def test_search_airport(self):
        self.authenticate(self.admin)
        url = reverse("airport:airport-list")
        response = self.client.get(url, {"search": "Boryspil"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.airports if "Boryspil" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)

    def test_search_airport_user(self):
        self.authenticate(self.user)
        url = reverse("airport:airport-list")
        response = self.client.get(url, {"search": "Lviv"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.airports if "Lviv" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)

    def test_ordering_airport(self):
        self.authenticate(self.admin)
        url = reverse("airport:airport-list")
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sorted_by_name = sorted(self.airports, key=lambda x: x.name)
        response_names = [t["name"] for t in response.data]
        expected_names = [t.name for t in sorted_by_name]
        self.assertEqual(response_names, expected_names)

    def test_filter_city(self):
        self.authenticate(self.admin)
        url = reverse("airport:airport-list")
        response = self.client.get(url, {"city": self.city1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [a for a in self.airports if a.closest_big_city_id == self.city1.id]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(a["id"] == obj.id for a in response.data)
            self.assertTrue(found)

    def test_filter_country(self):
        self.authenticate(self.admin)
        url = reverse("airport:airport-list")
        response = self.client.get(url, {"country": self.country.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [
            a for a in self.airports if a.closest_big_city.country_id == self.country.id
        ]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(a["id"] == obj.id for a in response.data)
            self.assertTrue(found)
