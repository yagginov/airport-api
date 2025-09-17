from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from airport.models import City, Country

User = get_user_model()

class TestCityApi(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username="admin", password="p", is_staff=True)
        cls.user = User.objects.create_user(username="user", password="p")
        cls.country1 = Country.objects.create(name="Ukraine")
        cls.country2 = Country.objects.create(name="Poland")
        cls.cities = [
            City.objects.create(name="Kyiv", country=cls.country1, is_capital=True, timezone="Europe/Kiev"),
            City.objects.create(name="Lviv", country=cls.country1, is_capital=False, timezone="Europe/Kiev"),
            City.objects.create(name="Warsaw", country=cls.country2, is_capital=True, timezone="Europe/Warsaw"),
        ]

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def test_list_cities_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:city-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        names = sorted([t["name"] for t in response.data])
        expected = sorted([t.name for t in self.cities])
        self.assertEqual(names, expected)

    def test_list_cities_user(self):
        self.authenticate(self.user)
        url = reverse("airport:city-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_cities_anon(self):
        url = reverse("airport:city-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_city_admin(self):
        self.authenticate(self.admin)
        obj = self.cities[0]
        url = reverse("airport:city-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_city_user(self):
        self.authenticate(self.user)
        obj = self.cities[1]
        url = reverse("airport:city-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_city_anon(self):
        obj = self.cities[2]
        url = reverse("airport:city-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_city_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:city-list")
        data = {"name": "Odessa", "country": self.country1.id, "is_capital": False, "timezone": "Europe/Kiev"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(City.objects.filter(name="Odessa").exists())

    def test_create_city_user(self):
        self.authenticate(self.user)
        url = reverse("airport:city-list")
        data = {"name": "Krakow", "country": self.country2.id, "is_capital": False, "timezone": "Europe/Warsaw"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(City.objects.filter(name="Krakow").exists())

    def test_create_city_anon(self):
        url = reverse("airport:city-list")
        data = {"name": "Dnipro", "country": self.country1.id, "is_capital": False, "timezone": "Europe/Kiev"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(City.objects.filter(name="Dnipro").exists())

    def test_update_city_admin(self):
        self.authenticate(self.admin)
        obj = self.cities[0]
        url = reverse("airport:city-detail", args=[obj.id])
        data = {"name": "Kyiv Updated", "country": self.country1.id, "is_capital": True, "timezone": "Europe/Kiev"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj.refresh_from_db()
        self.assertEqual(obj.name, "Kyiv Updated")

    def test_update_city_user(self):
        self.authenticate(self.user)
        obj = self.cities[1]
        url = reverse("airport:city-detail", args=[obj.id])
        data = {"name": "Lviv Updated", "country": self.country1.id, "is_capital": False, "timezone": "Europe/Kiev"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Lviv Updated")

    def test_update_city_anon(self):
        obj = self.cities[2]
        url = reverse("airport:city-detail", args=[obj.id])
        data = {"name": "Warsaw Updated", "country": self.country2.id, "is_capital": True, "timezone": "Europe/Warsaw"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Warsaw Updated")

    def test_delete_city_admin(self):
        self.authenticate(self.admin)
        obj = self.cities[2]
        url = reverse("airport:city-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(City.objects.filter(id=obj.id).exists())

    def test_delete_city_user(self):
        self.authenticate(self.user)
        obj = self.cities[1]
        url = reverse("airport:city-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(City.objects.filter(id=obj.id).exists())

    def test_delete_city_anon(self):
        obj = self.cities[0]
        url = reverse("airport:city-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(City.objects.filter(id=obj.id).exists())

    def test_search_city(self):
        self.authenticate(self.admin)
        url = reverse("airport:city-list")
        response = self.client.get(url, {"search": "Kyiv"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.cities if "Kyiv" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)

    def test_search_city_user(self):
        self.authenticate(self.user)
        url = reverse("airport:city-list")
        response = self.client.get(url, {"search": "Warsaw"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.cities if "Warsaw" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)

    def test_ordering_city(self):
        self.authenticate(self.admin)
        url = reverse("airport:city-list")
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sorted_by_name = sorted(self.cities, key=lambda x: x.name)
        response_names = [t["name"] for t in response.data]
        expected_names = [t.name for t in sorted_by_name]
        self.assertEqual(response_names, expected_names)

    def test_filter_country(self):
        self.authenticate(self.admin)
        url = reverse("airport:city-list")
        response = self.client.get(url, {"country": self.country1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [c for c in self.cities if c.country_id == self.country1.id]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            found = any(c["id"] == obj.id for c in response.data)
            self.assertTrue(found)