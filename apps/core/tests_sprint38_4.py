from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


class LimparDemoLegadoTests(TestCase):

    def test_remove_registros_legados(self):
        prestacao = Prestacao.objects.create(
            numtermo="LEGADO/2026",
            credor="OSC Exemplo ? Demonstra??o",
            valorContrato=1000,
        )

        termo = Termos.objects.create(
            numtermo="LEGADO/2026",
            valorglobal=1000,
        )

        empresa = Empresa.objects.create(
            nome="OSC Exemplo ? Demonstra??o",
            prestacao=prestacao,
            termos=termo,
        )

        saida = StringIO()

        call_command(
            "limpar_demo_legado",
            stdout=saida,
        )

        self.assertFalse(
            Empresa.objects.filter(pk=empresa.pk).exists()
        )
        self.assertFalse(
            Prestacao.objects.filter(pk=prestacao.pk).exists()
        )
        self.assertFalse(
            Termos.objects.filter(pk=termo.pk).exists()
        )

    def test_preserva_registros_demo_atuais(self):
        prestacao = Prestacao.objects.create(
            numtermo="ATUAL/2026",
            credor="OSC Exemplo ? Demo",
            valorContrato=2000,
        )

        termo = Termos.objects.create(
            numtermo="ATUAL/2026",
            valorglobal=2000,
        )

        empresa = Empresa.objects.create(
            nome="OSC Exemplo ? Demo",
            prestacao=prestacao,
            termos=termo,
        )

        call_command(
            "limpar_demo_legado",
            stdout=StringIO(),
        )

        self.assertTrue(
            Empresa.objects.filter(pk=empresa.pk).exists()
        )
        self.assertTrue(
            Prestacao.objects.filter(pk=prestacao.pk).exists()
        )
        self.assertTrue(
            Termos.objects.filter(pk=termo.pk).exists()
        )

    def test_comando_e_idempotente(self):
        saida1 = StringIO()
        saida2 = StringIO()

        call_command(
            "limpar_demo_legado",
            stdout=saida1,
        )

        call_command(
            "limpar_demo_legado",
            stdout=saida2,
        )

        self.assertIn(
            "Nenhum registro legado encontrado.",
            saida2.getvalue(),
        )
