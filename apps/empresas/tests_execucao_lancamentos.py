from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento


class EmpresaExecucaoLancamentosTests(TestCase):
    def setUp(self):
        self.empresa_a = Empresa.objects.create(
            nome="OSC A",
        )
        self.empresa_b = Empresa.objects.create(
            nome="OSC B",
        )

        Lancamento.objects.create(
            empresa=self.empresa_a,
            numero_lancamento="A-001",
            data_documento=date(2026, 9, 1),
            descricao="Despesa A1",
            valor_documento=Decimal("100.00"),
            valor_glosa=Decimal("20.00"),
            situacao=Lancamento.Situacao.REGULAR,
        )

        Lancamento.objects.create(
            empresa=self.empresa_a,
            numero_lancamento="A-002",
            data_documento=date(2026, 9, 2),
            descricao="Despesa A2",
            valor_documento=Decimal("50.00"),
            situacao=Lancamento.Situacao.NAO_ANALISADO,
        )

        Lancamento.objects.create(
            empresa=self.empresa_b,
            numero_lancamento="B-001",
            data_documento=date(2026, 9, 3),
            descricao="Despesa B1",
            valor_documento=Decimal("900.00"),
            situacao=Lancamento.Situacao.NAO_ANALISADO,
        )

    def test_total_ordens_isolado_por_empresa(self):
        self.assertEqual(
            self.empresa_a.totalOrdens,
            2,
        )
        self.assertEqual(
            self.empresa_b.totalOrdens,
            1,
        )

    def test_ordens_valor_isolado_por_empresa(self):
        self.assertEqual(
            self.empresa_a.ordensValor,
            Decimal("150.00"),
        )
        self.assertEqual(
            self.empresa_b.ordensValor,
            Decimal("900.00"),
        )

    def test_ordens_conferir_isolado_por_empresa(self):
        self.assertEqual(
            self.empresa_a.ordensConferir,
            1,
        )
        self.assertEqual(
            self.empresa_b.ordensConferir,
            1,
        )

    def test_valor_total_execucao_usa_valor_documento(self):
        self.assertEqual(
            self.empresa_a.valorTotalExecucao,
            Decimal("150.00"),
        )

        # A glosa nao reduz a despesa executada/documentada.
        lancamento = self.empresa_a.lancamentos.get(
            numero_lancamento="A-001",
        )

        self.assertEqual(
            lancamento.valor_aprovado,
            Decimal("80.00"),
        )

        self.assertEqual(
            self.empresa_a.valorTotalExecucao,
            Decimal("150.00"),
        )

    def test_despesa_total_usa_lancamentos_da_empresa(self):
        self.assertEqual(
            self.empresa_a.despesaTotal,
            Decimal("150.00"),
        )
        self.assertEqual(
            self.empresa_b.despesaTotal,
            Decimal("900.00"),
        )

    def test_saldo_financeiro_usa_lancamentos_da_empresa(self):
        self.assertEqual(
            self.empresa_a.saldoFinanceiro,
            Decimal("-150.00"),
        )
        self.assertEqual(
            self.empresa_b.saldoFinanceiro,
            Decimal("-900.00"),
        )
