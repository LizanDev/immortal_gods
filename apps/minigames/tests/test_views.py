"""Tests for minigames views."""

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.core.models import PlayerProfile


@override_settings(SECURE_SSL_REDIRECT=False)
class MinigamesIndexTest(TestCase):
    """Tests for the minigames hub page."""

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        PlayerProfile.objects.get_or_create(user=self.user)

    def test_index_returns_200_for_logged_in_user(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("minigames:index"))
        self.assertEqual(response.status_code, 200)

    def test_index_contains_expected_content(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("minigames:index"))
        self.assertContains(response, "Minijuegos")
        self.assertContains(response, "Memoria de Dioses")
        self.assertContains(response, "Rueda de la Fortuna")
