from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.metas.models import MetaExecucao
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


class LimparDemoLegadoTests(TestCase):

    def _criar_cenario_atual(
        self,
        numero,
        nome_empresa,
        credor,
        valor,
    ):
        prestacao = Prestacao.objects.create(
            numtermo=numero,
            credor=credor,
            valorContrato=valor,
        )

        termo = Termos.objects.create(
            numtermo=numero,
            valorglobal=valor,
        )

        empresa = Empresa.objects.create(
            nome=nome_empresa,
            prestacao=prestacao,
            termos=termo,
        )

        prestacao.empresa = empresa
        prestacao.save(update_fields=["empresa"])

        termo.empresa = empresa
        termo.save(update_fields=["empresa"])

        return empresa, prestacao, termo

    def test_remove_registros_demonstracao(self):
        prestacao = Prestacao.objects.create(
            numtermo="001/2026",
            credor="Instituto Caminhos ? Demonstra??o",
            valorContrato=240000,
        )

        termo = Termos.objects.create(
            numtermo="001/2026",
            valorglobal=240000,
        )

        empresa = Empresa.objects.create(
            nome="Instituto Caminhos ? Demonstra??o",
            prestacao=prestacao,
            termos=termo,
        )

        call_command(
            "limpar_demo_legado",
            stdout=StringIO(),
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

    def test_remove_registros_ficticios(self):
        prestacao = Prestacao.objects.create(
            numtermo="002/2026",
            credor="OSC Ficticia",
            valorContrato=120000,
        )

        termo = Termos.objects.create(
            numtermo="002/2026",
            valorglobal=120000,
        )

        empresa = Empresa.objects.create(
            nome="OSC Ficticia",
            prestacao=prestacao,
            termos=termo,
        )

        call_command(
            "limpar_demo_legado",
            stdout=StringIO(),
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

    def test_preserva_tres_cenarios_atuais(self):
        cenarios = (
            (
                "001/2026",
                "Prefeitura de Vale Sereno ? Demo",
                "Instituto Caminhos ? Demo",
                390000,
            ),
            (
                "002/2026",
                "Prefeitura de Nova Esperan?a ? Demo",
                "Associa??o Rede Cidad? ? Demo",
                420000,
            ),
            (
                "003/2026",
                "Prefeitura de Jardim das ?guas ? Demo",
                "Funda??o Sementes das ?guas ? Demo",
                450000,
            ),
        )

        criados = [
            self._criar_cenario_atual(*cenario)
            for cenario in cenarios
        ]

        call_command(
            "limpar_demo_legado",
            stdout=StringIO(),
        )

        for empresa, prestacao, termo in criados:
            self.assertTrue(
                Empresa.objects.filter(pk=empresa.pk).exists()
            )
            self.assertTrue(
                Prestacao.objects.filter(pk=prestacao.pk).exists()
            )
            self.assertTrue(
                Termos.objects.filter(pk=termo.pk).exists()
            )

    def test_remove_duplicidade_e_preserva_atual(self):
        atual_empresa, atual_prestacao, atual_termo = (
            self._criar_cenario_atual(
                "001/2026",
                "Prefeitura de Vale Sereno ? Demo",
                "Instituto Caminhos ? Demo",
                390000,
            )
        )

        antiga_prestacao = Prestacao.objects.create(
            numtermo="001/2026",
            credor="Instituto Caminhos de Vale Sereno ? Demonstra??o",
            valorContrato=390000,
        )

        antigo_termo = Termos.objects.create(
            numtermo="001/2026",
            valorglobal=390000,
        )

        antiga_empresa = Empresa.objects.create(
            nome="Prefeitura Municipal de Vale Sereno ? Demonstra??o",
            prestacao=antiga_prestacao,
            termos=antigo_termo,
        )

        call_command(
            "limpar_demo_legado",
            stdout=StringIO(),
        )

        self.assertTrue(
            Empresa.objects.filter(pk=atual_empresa.pk).exists()
        )
        self.assertTrue(
            Prestacao.objects.filter(pk=atual_prestacao.pk).exists()
        )
        self.assertTrue(
            Termos.objects.filter(pk=atual_termo.pk).exists()
        )

        self.assertFalse(
            Empresa.objects.filter(pk=antiga_empresa.pk).exists()
        )
        self.assertFalse(
            Prestacao.objects.filter(pk=antiga_prestacao.pk).exists()
        )
        self.assertFalse(
            Termos.objects.filter(pk=antigo_termo.pk).exists()
        )

    def test_remove_meta_excedente_do_cenario_atual(self):
        empresa, prestacao, termo = self._criar_cenario_atual(
            "001/2026",
            "Prefeitura de Vale Sereno ? Demo",
            "Instituto Caminhos ? Demo",
            390000,
        )

        for codigo in ("M1.1", "M1.2", "M1.3", "M1.EXTRA"):
            MetaExecucao.objects.create(
                prestacao=prestacao,
                codigo=codigo,
                descricao=f"Meta {codigo}",
                valor_previsto=100,
            )

        call_command(
            "limpar_demo_legado",
            stdout=StringIO(),
        )

        codigos = set(
            MetaExecucao.objects.filter(
                prestacao=prestacao
            ).values_list("codigo", flat=True)
        )

        self.assertEqual(
            codigos,
            {"M1.1", "M1.2", "M1.3"},
        )

    def test_comando_e_idempotente(self):
        call_command(
            "limpar_demo_legado",
            stdout=StringIO(),
        )

        saida = StringIO()

        call_command(
            "limpar_demo_legado",
            stdout=saida,
        )

        self.assertIn(
            "Higienizacao definitiva da base demo concluida.",
            saida.getvalue(),
        )
