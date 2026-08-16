from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from apps.diligencias.models import Diligencia
from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.metas.models import MetaExecucao
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


class PrepararDemoSeguroSprint40Tests(TestCase):

    def test_preparar_demo_nao_chama_limpeza_legada(self):
        with patch(
            "apps.core.management.commands.preparar_demo.call_command"
        ) as chamada:
            call_command(
                "preparar_demo",
                stdout=StringIO(),
            )

        comandos = [
            args[0]
            for args, kwargs in chamada.call_args_list
            if args
        ]

        self.assertIn(
            "preparar_demo_ciclo_completo",
            comandos,
        )
        self.assertNotIn(
            "limpar_demo_legado",
            comandos,
        )

    def test_preparar_demo_e_idempotente(self):
        call_command(
            "preparar_demo",
            stdout=StringIO(),
        )

        call_command(
            "preparar_demo",
            stdout=StringIO(),
        )

        self.assertEqual(Empresa.objects.count(), 3)
        self.assertEqual(Termos.objects.count(), 3)
        self.assertEqual(Prestacao.objects.count(), 3)
        self.assertEqual(Lancamento.objects.count(), 99)
        self.assertEqual(MetaExecucao.objects.count(), 9)
        self.assertEqual(Diligencia.objects.count(), 2)

    def test_preparar_demo_preserva_registro_externo(self):
        empresa_externa = Empresa.objects.create(
            nome="Empresa externa de teste"
        )

        call_command(
            "preparar_demo",
            stdout=StringIO(),
        )

        self.assertTrue(
            Empresa.objects.filter(
                pk=empresa_externa.pk
            ).exists()
        )

        self.assertEqual(
            Empresa.objects.count(),
            4,
        )

    def test_cenarios_padrao_permanecem_unicos(self):
        call_command(
            "preparar_demo",
            stdout=StringIO(),
        )

        call_command(
            "preparar_demo",
            stdout=StringIO(),
        )

        for numero in (
            "001/2026",
            "002/2026",
            "003/2026",
        ):
            with self.subTest(termo=numero):
                self.assertEqual(
                    Termos.objects.filter(
                        numtermo=numero
                    ).count(),
                    1,
                )

                self.assertEqual(
                    Prestacao.objects.filter(
                        numtermo=numero
                    ).count(),
                    1,
                )
