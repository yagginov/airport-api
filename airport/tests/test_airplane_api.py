from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from airport.models import Airplane, AirplaneType

User = get_user_model()


class TestAirplaneApi(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username="admin", password="p", is_staff=True
        )
        cls.user = User.objects.create_user(username="user", password="p")
        cls.type1 = AirplaneType.objects.create(name="Boeing 737")
        cls.type2 = AirplaneType.objects.create(name="Airbus A320")
        cls.airplanes = [
            Airplane.objects.create(
                name="Boeing 737-800", rows=30, seats_in_row=6, airplane_type=cls.type1
            ),
            Airplane.objects.create(
                name="Boeing 737-900", rows=32, seats_in_row=6, airplane_type=cls.type1
            ),
            Airplane.objects.create(
                name="Airbus A320neo", rows=28, seats_in_row=6, airplane_type=cls.type2
            ),
        ]

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def test_list_airplanes_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:aiplane-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        names = sorted([t["name"] for t in response.data])
        expected = sorted([t.name for t in self.airplanes])
        self.assertEqual(names, expected)

    def test_list_airplanes_user(self):
        self.authenticate(self.user)
        url = reverse("airport:aiplane-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_airplanes_anon(self):
        url = reverse("airport:aiplane-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_airplane_admin(self):
        self.authenticate(self.admin)
        obj = self.airplanes[0]
        url = reverse("airport:aiplane-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_airplane_user(self):
        self.authenticate(self.user)
        obj = self.airplanes[1]
        url = reverse("airport:aiplane-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], obj.name)

    def test_retrieve_airplane_anon(self):
        obj = self.airplanes[2]
        url = reverse("airport:aiplane-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_airplane_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:aiplane-list")
        data = {
            "name": "Boeing 737 MAX",
            "rows": 33,
            "seats_in_row": 6,
            "airplane_type": self.type1.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Airplane.objects.filter(name="Boeing 737 MAX").exists())

    def test_create_airplane_user(self):
        self.authenticate(self.user)
        url = reverse("airport:aiplane-list")
        data = {
            "name": "Airbus A321",
            "rows": 34,
            "seats_in_row": 6,
            "airplane_type": self.type2.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Airplane.objects.filter(name="Airbus A321").exists())

    def test_create_airplane_anon(self):
        url = reverse("airport:aiplane-list")
        data = {
            "name": "Embraer E190",
            "rows": 25,
            "seats_in_row": 4,
            "airplane_type": self.type2.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Airplane.objects.filter(name="Embraer E190").exists())

    def test_update_airplane_admin(self):
        self.authenticate(self.admin)
        obj = self.airplanes[0]
        url = reverse("airport:aiplane-detail", args=[obj.id])
        data = {
            "name": "Boeing 737-800 Updated",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": self.type1.id,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj.refresh_from_db()
        self.assertEqual(obj.name, "Boeing 737-800 Updated")

    def test_update_airplane_user(self):
        self.authenticate(self.user)
        obj = self.airplanes[1]
        url = reverse("airport:aiplane-detail", args=[obj.id])
        data = {
            "name": "Boeing 737-900 Updated",
            "rows": 32,
            "seats_in_row": 6,
            "airplane_type": self.type1.id,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Boeing 737-900 Updated")

    def test_update_airplane_anon(self):
        obj = self.airplanes[2]
        url = reverse("airport:aiplane-detail", args=[obj.id])
        data = {
            "name": "Airbus A320neo Updated",
            "rows": 28,
            "seats_in_row": 6,
            "airplane_type": self.type2.id,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        obj.refresh_from_db()
        self.assertNotEqual(obj.name, "Airbus A320neo Updated")

    def test_delete_airplane_admin(self):
        self.authenticate(self.admin)
        obj = self.airplanes[2]
        url = reverse("airport:aiplane-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Airplane.objects.filter(id=obj.id).exists())

    def test_delete_airplane_user(self):
        self.authenticate(self.user)
        obj = self.airplanes[1]
        url = reverse("airport:aiplane-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Airplane.objects.filter(id=obj.id).exists())

    def test_delete_airplane_anon(self):
        obj = self.airplanes[0]
        url = reverse("airport:aiplane-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Airplane.objects.filter(id=obj.id).exists())

    def test_search_airplane(self):
        self.authenticate(self.admin)
        url = reverse("airport:aiplane-list")
        response = self.client.get(url, {"search": "Boeing"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.airplanes if "Boeing" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)

    def test_search_airplane_user(self):
        self.authenticate(self.user)
        url = reverse("airport:aiplane-list")
        response = self.client.get(url, {"search": "Airbus"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [t for t in self.airplanes if "Airbus" in t.name]
        response_names = [t["name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.name, response_names)

    def test_ordering_airplane(self):
        self.authenticate(self.admin)
        url = reverse("airport:aiplane-list")
        response = self.client.get(url, {"ordering": "capacity"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sorted_by_capacity = sorted(
            self.airplanes, key=lambda x: x.rows * x.seats_in_row
        )
        response_names = [t["name"] for t in response.data]
        expected_names = [t.name for t in sorted_by_capacity]
        self.assertEqual(response_names, expected_names)
