import os
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.metas.models import MetaExecucao
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


class ResetarDemoTests(TestCase):

    def test_reset_bloqueado_sem_variavel(self):
        with patch.dict(
            os.environ,
            {"PGP_DEMO_RESET_ALLOWED": ""},
            clear=False,
        ):
            with self.assertRaises(CommandError):
                call_command(
                    "resetar_demo",
                    stdout=StringIO(),
                )

    def test_reset_recria_base_padrao(self):
        with patch.dict(
            os.environ,
            {"PGP_DEMO_RESET_ALLOWED": "1"},
            clear=False,
        ):
            call_command(
                "resetar_demo",
                stdout=StringIO(),
            )

        self.assertEqual(Empresa.objects.count(), 3)
        self.assertEqual(Termos.objects.count(), 3)
        self.assertEqual(Prestacao.objects.count(), 3)
        self.assertEqual(Lancamento.objects.count(), 99)
        self.assertEqual(MetaExecucao.objects.count(), 9)

        self.assertEqual(
            Prestacao.objects.filter(
                numtermo="001/2026"
            ).count(),
            1,
        )
        self.assertEqual(
            Prestacao.objects.filter(
                numtermo="002/2026"
            ).count(),
            1,
        )
        self.assertEqual(
            Prestacao.objects.filter(
                numtermo="003/2026"
            ).count(),
            1,
        )

    def test_reset_e_idempotente(self):
        with patch.dict(
            os.environ,
            {"PGP_DEMO_RESET_ALLOWED": "1"},
            clear=False,
        ):
            call_command(
                "resetar_demo",
                stdout=StringIO(),
            )

            call_command(
                "resetar_demo",
                stdout=StringIO(),
            )

        self.assertEqual(Empresa.objects.count(), 3)
        self.assertEqual(Termos.objects.count(), 3)
        self.assertEqual(Prestacao.objects.count(), 3)
        self.assertEqual(Lancamento.objects.count(), 99)
        self.assertEqual(MetaExecucao.objects.count(), 9)
