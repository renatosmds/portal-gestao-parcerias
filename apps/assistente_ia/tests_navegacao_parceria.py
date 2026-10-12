import os
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.documentos.models import Documento

from .models import ProcessamentoAssistido


class NavegacaoParceriaAssistenteIATests(TestCase):

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

        cls.documento = (
            Documento.objects
            .filter(
                termo__numtermo="001/2026",
            )
            .select_related(
                "termo",
                "empresa",
            )
            .order_by("pk")
            .first()
        )

        cls.processamento = (
            ProcessamentoAssistido.objects.create(
                documento=cls.documento,
                empresa=cls.documento.empresa,
                solicitado_por=cls.usuario,
                resumo="Teste de navegacao.",
            )
        )

    def setUp(self):
        self.client.force_login(
            self.usuario
        )

    def test_detalhe_exibe_atalho_parceria(self):
        response = self.client.get(
            reverse(
                "assistente_ia_detalhe",
                kwargs={
                    "pk": self.processamento.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Abrir parceria",
        )

        parceria = response.context[
            "parceria"
        ]

        self.assertIsNotNone(
            parceria
        )

        self.assertEqual(
            parceria.numtermo_id,
            self.documento.termo_id,
        )

    def test_central_exibe_atalho_parceria(self):
        response = self.client.get(
            reverse(
                "assistente_ia_central"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Abrir parceria",
        )

        self.assertContains(
            response,
            "Ver análise",
        )
