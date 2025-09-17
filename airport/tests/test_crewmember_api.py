from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

from airport.models import CrewMember

User = get_user_model()

class TestCrewMemberApi(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username="admin", password="p", is_staff=True)
        cls.user = User.objects.create_user(username="user", password="p")
        cls.crew_members = [
            CrewMember.objects.create(first_name="Ivan", last_name="Ivanov"),
            CrewMember.objects.create(first_name="Petro", last_name="Petrenko"),
            CrewMember.objects.create(first_name="Anna", last_name="Shevchenko"),
        ]

    def authenticate(self, user):
        self.client.force_authenticate(user)

    def test_list_crew_members_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:crew-member-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        names = sorted([t["full_name"] for t in response.data])
        expected = sorted([cm.full_name for cm in self.crew_members])
        self.assertEqual(names, expected)

    def test_list_crew_members_user(self):
        self.authenticate(self.user)
        url = reverse("airport:crew-member-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_crew_members_anon(self):
        url = reverse("airport:crew-member-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_crew_member_admin(self):
        self.authenticate(self.admin)
        obj = self.crew_members[0]
        url = reverse("airport:crew-member-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], obj.full_name)

    def test_retrieve_crew_member_user(self):
        self.authenticate(self.user)
        obj = self.crew_members[1]
        url = reverse("airport:crew-member-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], obj.full_name)

    def test_retrieve_crew_member_anon(self):
        obj = self.crew_members[2]
        url = reverse("airport:crew-member-detail", args=[obj.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_crew_member_admin(self):
        self.authenticate(self.admin)
        url = reverse("airport:crew-member-list")
        data = {"first_name": "Olga", "last_name": "Koval"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CrewMember.objects.filter(first_name="Olga", last_name="Koval").exists())

    def test_create_crew_member_user(self):
        self.authenticate(self.user)
        url = reverse("airport:crew-member-list")
        data = {"first_name": "Dmytro", "last_name": "Bondarenko"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(CrewMember.objects.filter(first_name="Dmytro", last_name="Bondarenko").exists())

    def test_create_crew_member_anon(self):
        url = reverse("airport:crew-member-list")
        data = {"first_name": "Svitlana", "last_name": "Kravets"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(CrewMember.objects.filter(first_name="Svitlana", last_name="Kravets").exists())

    def test_update_crew_member_admin(self):
        self.authenticate(self.admin)
        obj = self.crew_members[0]
        url = reverse("airport:crew-member-detail", args=[obj.id])
        data = {"first_name": "Ivan Updated", "last_name": "Ivanov"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj.refresh_from_db()
        self.assertEqual(obj.first_name, "Ivan Updated")

    def test_update_crew_member_user(self):
        self.authenticate(self.user)
        obj = self.crew_members[1]
        url = reverse("airport:crew-member-detail", args=[obj.id])
        data = {"first_name": "Petro Updated", "last_name": "Petrenko"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        obj.refresh_from_db()
        self.assertNotEqual(obj.first_name, "Petro Updated")

    def test_update_crew_member_anon(self):
        obj = self.crew_members[2]
        url = reverse("airport:crew-member-detail", args=[obj.id])
        data = {"first_name": "Anna Updated", "last_name": "Shevchenko"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        obj.refresh_from_db()
        self.assertNotEqual(obj.first_name, "Anna Updated")

    def test_delete_crew_member_admin(self):
        self.authenticate(self.admin)
        obj = self.crew_members[2]
        url = reverse("airport:crew-member-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CrewMember.objects.filter(id=obj.id).exists())

    def test_delete_crew_member_user(self):
        self.authenticate(self.user)
        obj = self.crew_members[1]
        url = reverse("airport:crew-member-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CrewMember.objects.filter(id=obj.id).exists())

    def test_delete_crew_member_anon(self):
        obj = self.crew_members[0]
        url = reverse("airport:crew-member-detail", args=[obj.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(CrewMember.objects.filter(id=obj.id).exists())

    def test_search_crew_member(self):
        self.authenticate(self.admin)
        url = reverse("airport:crew-member-list")
        response = self.client.get(url, {"search": "Ivan"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered = [cm for cm in self.crew_members if "Ivan" in cm.first_name or "Ivan" in cm.last_name]
        response_names = [t["full_name"] for t in response.data]
        self.assertEqual(len(response.data), len(filtered))
        for obj in filtered:
            self.assertIn(obj.full_name, response_names)

    def test_ordering_crew_member(self):
        self.authenticate(self.admin)
        url = reverse("airport:crew-member-list")
        response = self.client.get(url, {"ordering": "first_name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sorted_by_first_name = sorted(self.crew_members, key=lambda x: x.first_name)
        response_names = [t["full_name"] for t in response.data]
        expected_names = [cm.full_name for cm in sorted_by_first_name]
        self.assertEqual(response_names, expected_names)
