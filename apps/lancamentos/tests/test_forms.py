from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.forms import LancamentoForm
from apps.lancamentos.models import Lancamento


class LancamentoFormTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nome="Empresa Formulário")

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
