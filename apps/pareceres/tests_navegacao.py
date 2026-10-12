import os
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.pareceres.models import ParecerTecnico
from apps.prestacao.models import Prestacao


class NavegacaoParecerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command(
            "preparar_demo_ciclo_completo",
            verbosity=0,
        )

        User = get_user_model()

        cls.usuario = User.objects.get(
            username=os.getenv("DEMO_ADMIN_USERNAME", "demo_admin")
        )

        cls.prestacao = Prestacao.objects.get(
            numtermo="001/2026"
        )

        cls.parecer = ParecerTecnico.objects.create(
            prestacao=cls.prestacao,
            empresa=cls.prestacao.empresa,
            numero="PT-NAVEGACAO",
            elaborado_por=cls.usuario,
        )

    def setUp(self):
        self.client.force_login(
            self.usuario
        )

    def test_detalhe_exibe_botoes_de_navegacao(self):
        response = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Voltar aos Pareceres",
        )

        self.assertContains(
            response,
            "Abrir Prestação",
        )

        self.assertContains(
            response,
            "Abrir Parceria",
        )

        self.assertIsNotNone(
            response.context["parceria"]
        )

    def test_revisao_exibe_botoes_de_navegacao(self):
        response = self.client.get(
            reverse(
                "pareceres:parecer_revisar",
                args=[self.parecer.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Voltar ao Parecer",
        )

        self.assertContains(
            response,
            "Abrir Prestação",
        )

        self.assertContains(
            response,
            "Abrir Parceria",
        )
