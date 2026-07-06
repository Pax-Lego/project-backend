import json

from django.test import Client, TestCase
from django.urls import reverse

from apps.accounts.models import CustomUser


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.me_url = reverse("current_user")

    def test_user_registration(self):
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }
        response = self.client.post(
            self.register_url, data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(email="test@example.com").exists())

    def test_user_registration_password_mismatch(self):
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "password_confirm": "wrongpass",
        }
        response = self.client.post(
            self.register_url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_user_login(self):
        user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(
            self.login_url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("sessionid", self.client.cookies)

    def test_user_login_invalid_credentials(self):
        data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(
            self.login_url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

    def test_current_user_authenticated(self):
        user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], "test@example.com")

    def test_current_user_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 403)

    def test_user_logout(self):
        user = CustomUser.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
