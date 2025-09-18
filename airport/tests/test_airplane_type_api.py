from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from airport.models import AirplaneType

User = get_user_model()


class TestAirplaneType(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="admin", password="p", is_staff=True
        )
        cls.user = User.objects.create_user(username="user", password="p")
        cls.airplane_types = [
            AirplaneType.objects.create(name="Boeing 737"),
            AirplaneType.objects.create(name="Airbus A320"),
            AirplaneType.objects.create(name="Embraer 190"),
            AirplaneType.objects.create(name="Bombardier Q400"),
        ]

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def test_list_airplane_types_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:airplane-type-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        names = sorted([t["name"] for t in response.data])
        expected = sorted([t.name for t in self.airplane_types])
        self.assertEqual(names, expected)

    def test_list_airplane_types_user(self):
        self.authenticate(self.user)
        url = reverse("airport:airplane-type-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_list_airplane_types_anon(self):
        url = reverse("airport:airplane-type-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_airplane_type_admin(self):
        self.authenticate(self.admin)
        obj = self.airplane_types[0]
        url = reverse("airport:airplane-type-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_airplane_type_user(self):
        self.authenticate(self.user)
        obj = self.airplane_types[1]
        url = reverse("airport:airplane-type-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_airplane_type_anon(self):
        obj = self.airplane_types[2]
        url = reverse("airport:airplane-type-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_airplane_type_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:airplane-type-list")
        data = {"name": "Sukhoi Superjet"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AirplaneType.objects.filter(name="Sukhoi Superjet").exists())

    def test_create_airplane_type_user(self):
        self.authenticate(self.user)
        url = reverse("airport:airplane-type-list")
        data = {"name": "Tupolev Tu-154"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(AirplaneType.objects.filter(name="Tupolev Tu-154").exists())

    def test_create_airplane_type_anon(self):
        url = reverse("airport:airplane-type-list")
        data = {"name": "Antonov An-148"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(AirplaneType.objects.filter(name="Antonov An-148").exists())

    def test_update_airplane_type_admin(self):
        self.authenticate(self.admin)
        obj = self.airplane_types[0]
        url = reverse("airport:airplane-type-detail", args=[obj.id])
        data = {"name": "Boeing 777"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj.refresh_from_db()
        self.assertEqual(obj.name, "Boeing 777")

    def test_update_airplane_type_user(self):
        self.authenticate(self.user)
        obj = self.airplane_types[1]
        url = reverse("airport:airplane-type-detail", args=[obj.id])
        data = {"name": "Airbus A380"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Airbus A380")

    def test_update_airplane_type_anon(self):
        obj = self.airplane_types[2]
        url = reverse("airport:airplane-type-detail", args=[obj.id])
        data = {"name": "Embraer E195"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Embraer E195")

    def test_delete_airplane_type_admin(self):
        self.authenticate(self.admin)
        obj = self.airplane_types[3]
        url = reverse("airport:airplane-type-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AirplaneType.objects.filter(id=obj.id).exists())

    def test_delete_airplane_type_user(self):
        self.authenticate(self.user)
        obj = self.airplane_types[2]
        url = reverse("airport:airplane-type-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(AirplaneType.objects.filter(id=obj.id).exists())

    def test_delete_airplane_type_anon(self):
        obj = self.airplane_types[1]
        url = reverse("airport:airplane-type-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(AirplaneType.objects.filter(id=obj.id).exists())

    def test_search_airplane_type(self):
        self.authenticate(self.admin)
        url = reverse("airport:airplane-type-list")
        response = self.client.get(url, {"search": "Boeing"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.airplane_types if "Boeing" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)

    def test_search_airplane_type_user(self):
        self.authenticate(self.user)
        url = reverse("airport:airplane-type-list")
        response = self.client.get(url, {"search": "Airbus"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.airplane_types if "Airbus" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)
