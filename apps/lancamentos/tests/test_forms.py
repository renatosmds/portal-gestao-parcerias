from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.forms import LancamentoForm
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import CompetenciaPrestacao, Prestacao


class LancamentoFormTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nome="Empresa Formulário")

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            tipo="cnpj",
            numtermo="TESTE-001/2026",
        )

    def dados_validos(self):
        return {
            "numero_lancamento": "1001",
            "tipo_documento": Lancamento.TipoDocumento.NFE,
            "data_documento": date(2026, 7, 23),
            "descricao": "Material de consumo",
            "valor_documento": "100.00",
            "valor_glosa": "0.00",
            "situacao": Lancamento.Situacao.REGULAR,
            "atestado": True,
        }

    def test_glosa_nao_pode_superar_documento(self):
        dados = self.dados_validos()
        dados["valor_glosa"] = "120.00"
        form = LancamentoForm(data=dados, empresa=self.empresa)
        self.assertFalse(form.is_valid())
        self.assertIn("valor_glosa", form.errors)

    def test_reprovacao_exige_textos(self):
        dados = self.dados_validos()
        dados["situacao"] = Lancamento.Situacao.REPROVADO
        form = LancamentoForm(data=dados, empresa=self.empresa)
        self.assertFalse(form.is_valid())
        self.assertIn("justificativa", form.errors)
        self.assertIn("recomendacao", form.errors)

    def test_competencia_de_outra_prestacao_e_rejeitada(self):
        outra_prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            tipo="cnpj",
            numtermo="OUTRA-001/2026",
        )

        competencia_incorreta = CompetenciaPrestacao.objects.create(
            prestacao=outra_prestacao,
            ano=2026,
            mes=2,
            data_inicial=date(2026, 2, 1),
            data_final=date(2026, 2, 28),
        )

        dados = self.dados_validos()
        dados.update(
            {
                "prestacao": self.prestacao.pk,
                "competencia": competencia_incorreta.pk,
                "numero_lancamento": "TESTE-COMP-INVALIDA",
                "data_documento": "2026-01-15",
                "descricao": "Teste de competencia invalida",
            }
        )

        form = LancamentoForm(
            data=dados,
            empresa=self.empresa,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("competencia", form.errors)

    def test_competencia_da_mesma_prestacao_e_aceita(self):
        competencia_correta = CompetenciaPrestacao.objects.create(
            prestacao=self.prestacao,
            ano=2026,
            mes=1,
            data_inicial=date(2026, 1, 1),
            data_final=date(2026, 1, 31),
        )

        dados = self.dados_validos()
        dados.update(
            {
                "prestacao": self.prestacao.pk,
                "competencia": competencia_correta.pk,
                "numero_lancamento": "TESTE-COMP-VALIDA",
                "data_documento": "2026-01-15",
                "descricao": "Teste de competencia valida",
            }
        )

        form = LancamentoForm(
            data=dados,
            empresa=self.empresa,
        )

        self.assertTrue(
            form.is_valid(),
            form.errors.as_json(),
        )

