from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import CustomUser


class ProfileBmrExposureTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="bmruser", email="bmr@example.com", password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_bmr_is_null_when_profile_incomplete(self):
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("bmr", response.json())
        self.assertIsNone(response.json()["bmr"])

    def test_bmr_is_calculated_once_profile_and_weight_are_set(self):
        list_response = self.client.get("/api/profile/")
        profile_id = list_response.json()["id"]

        self.client.patch(
            f"/api/profile/{profile_id}/",
            {
                "sex": "male",
                "date_of_birth": "1998-07-11",
                "height_cm": 180,
                "activity_level": "moderate",
                "goal": "maintain",
            },
            format="json",
        )
        self.client.post(
            "/api/profile/weight/",
            {"weight_kg": 80, "date": date.today().isoformat()},
            format="json",
        )

        response = self.client.get("/api/profile/")
        data = response.json()

        # Mifflin-St Jeor for male: (10*80) + (6.25*180) - (5*age) + 5
        age = data["age"]
        expected_bmr = (10 * 80) + (6.25 * 180) - (5 * age) + 5
        self.assertAlmostEqual(data["bmr"], expected_bmr)
        self.assertIsNotNone(data["tdee"])
