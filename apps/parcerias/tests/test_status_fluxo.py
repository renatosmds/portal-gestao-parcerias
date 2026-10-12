from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.parcerias.models import Parcerias


class StatusFluxoParceriaTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command(
            "preparar_demo_ciclo_completo",
            verbosity=0,
        )

        User = get_user_model()

        cls.usuario = User.objects.get(
            username="homologador"
        )

        cls.parceria = (
            Parcerias.objects
            .select_related(
                "numtermo",
                "empresa",
            )
            .get(
                numtermo__numtermo="001/2026"
            )
        )

    def setUp(self):
        self.client.force_login(
            self.usuario
        )

    def test_resumos_existem(self):

        response = self.client.get(
            reverse(
                "detail_parceria",
                args=[self.parceria.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        fluxo = response.context[
            "fluxo_parceria"
        ]

        self.assertIn(
            "resumos",
            fluxo,
        )

        for chave in (
            "termo",
            "planos",
            "prestacoes",
            "lancamentos",
            "documentos",
            "conciliacoes",
            "diligencias",
            "processamentos",
            "pareceres",
        ):
            self.assertIn(
                chave,
                fluxo["resumos"],
            )

            self.assertTrue(
                fluxo["resumos"][chave]
            )

    def test_cards_estao_numerados_de_1_a_9(self):

        response = self.client.get(
            reverse(
                "detail_parceria",
                args=[self.parceria.pk],
            )
        )

        titulos = (
            "1. Termo",
            "2. Plano de Trabalho",
            "3. Presta\u00e7\u00e3o de Contas",
            "4. Lan\u00e7amentos",
            "5. Documentos",
            "6. Concilia\u00e7\u00e3o banc\u00e1ria",
            "7. Dilig\u00eancias",
            "8. An\u00e1lise Assistida",
            "9. Parecer T\u00e9cnico",
        )

        for titulo in titulos:
            self.assertContains(
                response,
                titulo,
            )

    def test_analise_assistida_vem_antes_do_parecer(self):

        response = self.client.get(
            reverse(
                "detail_parceria",
                args=[self.parceria.pk],
            )
        )

        html = response.content.decode(
            "utf-8"
        )

        titulo_analise = (
            "8. An\u00e1lise Assistida"
        )

        titulo_parecer = (
            "9. Parecer T\u00e9cnico"
        )

        self.assertIn(
            titulo_analise,
            html,
        )

        self.assertIn(
            titulo_parecer,
            html,
        )

        self.assertLess(
            html.index(
                titulo_analise
            ),
            html.index(
                titulo_parecer
            ),
        )


    def test_classes_visuais_dos_status(self):

        response = self.client.get(
            reverse(
                "detail_parceria",
                args=[self.parceria.pk],
            )
        )

        fluxo = response.context[
            "fluxo_parceria"
        ]

        self.assertIn(
            "classes_status",
            fluxo,
        )

        for chave in (
            "termo",
            "planos",
            "prestacoes",
            "lancamentos",
            "documentos",
            "conciliacoes",
            "diligencias",
            "processamentos",
            "pareceres",
        ):
            self.assertIn(
                chave,
                fluxo["classes_status"],
            )

            self.assertIn(
                fluxo["classes_status"][chave],
                {
                    "badge-success",
                    "badge-warning",
                    "badge-danger",
                    "badge-info",
                    "badge-secondary",
                    "badge-light",
                },
            )

    def test_classificacao_visual_nao_altera_regra_de_negocio(self):

        from apps.parcerias.fluxo import (
            _classe_status,
        )

        self.assertEqual(
            _classe_status("Regular: 33"),
            "badge-success",
        )

        self.assertEqual(
            _classe_status("Atendida: 1"),
            "badge-success",
        )

        self.assertEqual(
            _classe_status("Em revis\u00e3o: 1"),
            "badge-warning",
        )

        self.assertEqual(
            _classe_status("Em dilig\u00eancia: 1"),
            "badge-warning",
        )

        self.assertEqual(
            _classe_status("N\u00e3o atendida: 1"),
            "badge-danger",
        )

        self.assertEqual(
            _classe_status("Em an\u00e1lise: 1"),
            "badge-info",
        )

        self.assertEqual(
            _classe_status("Sem registros"),
            "badge-secondary",
        )
