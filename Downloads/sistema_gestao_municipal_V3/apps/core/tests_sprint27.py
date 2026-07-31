from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class Sprint27ConsolidacaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(
            username="homologador", password="teste-seguro-27", is_staff=True
        )

    def test_rotas_criticas_resolvem(self):
        for nome in (
            "home",
            "conciliacao_painel",
            "metas_painel",
            "assistente_ia_central",
            "relatorios_painel",
            "diagnostico_portal",
        ):
            with self.subTest(nome=nome):
                self.assertTrue(reverse(nome).startswith("/"))

    def test_diagnostico_exige_login_staff(self):
        resposta = self.client.get(reverse("diagnostico_portal"))
        self.assertEqual(resposta.status_code, 302)

    def test_staff_acessa_diagnostico(self):
        self.client.force_login(self.staff)
        resposta = self.client.get(reverse("diagnostico_portal"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Diagnóstico e homologação")
