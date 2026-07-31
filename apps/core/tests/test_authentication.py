from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from apps.core.views import home


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="teste_login",
            password="senha-segura-123",
        )

    def test_home_requires_authentication(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_login_page_opens(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_post_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_legacy_login_redirects_to_official_login(self):
        response = self.client.get(reverse("legacy_login"))
        self.assertRedirects(response, reverse("login"))

    def test_root_resolves_to_dashboard(self):
        self.assertIs(resolve("/").func, home)
