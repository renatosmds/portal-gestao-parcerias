from django.contrib.auth import get_user_model
from django.test import TestCase


class PrioridadesDashboardSprint37Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.usuario = User.objects.create_user(
            username="teste_sprint37",
            password="SenhaTeste123!",
            is_staff=True,
            is_superuser=True,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_dashboard_prioridades_carrega(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pendências que exigem atenção")

    def test_alertas_dashboard_possuem_novas_prioridades(self):
        response = self.client.get("/")

        alertas = response.context["alertas_dashboard"]
        rotulos = [alerta["rotulo"] for alerta in alertas]

        self.assertIn("Prestações em diligência", rotulos)
        self.assertIn("Metas atrasadas", rotulos)

    def test_rotas_das_novas_prioridades(self):
        response = self.client.get("/")

        alertas = response.context["alertas_dashboard"]

        por_rotulo = {
            alerta["rotulo"]: alerta
            for alerta in alertas
        }

        self.assertEqual(
            por_rotulo["Prestações em diligência"]["url_name"],
            "list_prestacao",
        )

        self.assertEqual(
            por_rotulo["Metas atrasadas"]["url_name"],
            "metas_painel",
        )

    def test_novas_prioridades_possuem_valores_numericos(self):
        response = self.client.get("/")

        alertas = response.context["alertas_dashboard"]

        por_rotulo = {
            alerta["rotulo"]: alerta
            for alerta in alertas
        }

        self.assertIsInstance(
            por_rotulo["Prestações em diligência"]["valor"],
            int,
        )

        self.assertIsInstance(
            por_rotulo["Metas atrasadas"]["valor"],
            int,
        )
