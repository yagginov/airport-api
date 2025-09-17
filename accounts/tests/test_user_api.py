from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUserApi(APITestCase):
    def test_register_valid(self):
        url = reverse("accounts:register")
        data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "testpass123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="validuser").exists())

    def test_register_username_with_space(self):
        url = reverse("accounts:register")
        data = {
            "username": "invalid user",
            "email": "user@example.com",
            "password": "testpass123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="invalid user").exists())

    def test_register_username_with_special_chars(self):
        url = reverse("accounts:register")
        data = {
            "username": "user!@#",
            "email": "user@example.com",
            "password": "testpass123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="user!@#").exists())

    def test_register_username_with_cyrillic(self):
        url = reverse("accounts:register")
        data = {
            "username": "юзер",
            "email": "user@example.com",
            "password": "testpass123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="юзер").exists())

    def test_register_short_password(self):
        url = reverse("accounts:register")
        data = {
            "username": "shortpassuser",
            "email": "user@example.com",
            "password": "123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="shortpassuser").exists())

    def test_profile_access_authenticated(self):
        user = User.objects.create_user(
            username="profileuser", password="testpass123", email="profile@example.com"
        )
        self.client.force_authenticate(user)
        url = reverse("accounts:user-detail")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "profileuser")

    def test_profile_access_unauthenticated(self):
        url = reverse("accounts:user-detail")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update(self):
        user = User.objects.create_user(
            username="updateuser", password="testpass123", email="update@example.com"
        )
        self.client.force_authenticate(user)
        url = reverse("accounts:user-detail")
        data = {"first_name": "Test", "last_name": "User"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

    def test_profile_delete(self):
        user = User.objects.create_user(
            username="deleteuser", password="testpass123", email="delete@example.com"
        )
        self.client.force_authenticate(user)
        url = reverse("accounts:user-detail")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username="deleteuser").exists())
