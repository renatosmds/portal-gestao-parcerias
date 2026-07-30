from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from django.urls import reverse


class Sprint21StaticFilesTests(SimpleTestCase):
    def test_css_principal_existe(self):
        self.assertTrue(finders.find("css/sgm-v2.css"))

    def test_css_login_existe(self):
        self.assertTrue(finders.find("css/login-v3.css"))

    def test_css_dashboard_existe(self):
        self.assertTrue(finders.find("css/dashboard-v3.css"))

    def test_login_referencia_css_estatico(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "/static/css/login-v3.css")
