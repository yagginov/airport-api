from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from airport.models import Country

User = get_user_model()

class TestCountryApi(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username="admin", password="p", is_staff=True)
        cls.user = User.objects.create_user(username="user", password="p")
        cls.countries = [
            Country.objects.create(name="Ukraine"),
            Country.objects.create(name="Poland"),
            Country.objects.create(name="Germany"),
        ]

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def test_list_countries_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:country-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        names = sorted([t["name"] for t in response.data])
        expected = sorted([t.name for t in self.countries])
        self.assertEqual(names, expected)

    def test_list_countries_user(self):
        self.authenticate(self.user)
        url = reverse("airport:country-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_countries_anon(self):
        url = reverse("airport:country-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_country_admin(self):
        self.authenticate(self.admin)
        obj = self.countries[0]
        url = reverse("airport:country-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_country_user(self):
        self.authenticate(self.user)
        obj = self.countries[1]
        url = reverse("airport:country-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_country_anon(self):
        obj = self.countries[2]
        url = reverse("airport:country-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_country_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:country-list")
        data = {"name": "France"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Country.objects.filter(name="France").exists())

    def test_create_country_user(self):
        self.authenticate(self.user)
        url = reverse("airport:country-list")
        data = {"name": "Italy"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Country.objects.filter(name="Italy").exists())

    def test_create_country_anon(self):
        url = reverse("airport:country-list")
        data = {"name": "Spain"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Country.objects.filter(name="Spain").exists())

    def test_update_country_admin(self):
        self.authenticate(self.admin)
        obj = self.countries[0]
        url = reverse("airport:country-detail", args=[obj.id])
        data = {"name": "Ukraine Updated"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj.refresh_from_db()
        self.assertEqual(obj.name, "Ukraine Updated")

    def test_update_country_user(self):
        self.authenticate(self.user)
        obj = self.countries[1]
        url = reverse("airport:country-detail", args=[obj.id])
        data = {"name": "Poland Updated"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Poland Updated")

    def test_update_country_anon(self):
        obj = self.countries[2]
        url = reverse("airport:country-detail", args=[obj.id])
        data = {"name": "Germany Updated"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Germany Updated")

    def test_delete_country_admin(self):
        self.authenticate(self.admin)
        obj = self.countries[2]
        url = reverse("airport:country-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Country.objects.filter(id=obj.id).exists())

    def test_delete_country_user(self):
        self.authenticate(self.user)
        obj = self.countries[1]
        url = reverse("airport:country-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Country.objects.filter(id=obj.id).exists())

    def test_delete_country_anon(self):
        obj = self.countries[0]
        url = reverse("airport:country-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Country.objects.filter(id=obj.id).exists())

    def test_search_country(self):
        self.authenticate(self.admin)
        url = reverse("airport:country-list")
        response = self.client.get(url, {"search": "Ukra"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.countries if "Ukra" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)

    def test_search_country_user(self):
        self.authenticate(self.user)
        url = reverse("airport:country-list")
        response = self.client.get(url, {"search": "Pol"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.countries if "Pol" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)

    def test_ordering_country(self):
        self.authenticate(self.admin)
        url = reverse("airport:country-list")
        response = self.client.get(url, {"ordering": "name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sorted_by_name = sorted(self.countries, key=lambda x: x.name)
        response_names = [t["name"] for t in response.data]
        expected_names = [t.name for t in sorted_by_name]
        self.assertEqual(response_names, expected_names)
