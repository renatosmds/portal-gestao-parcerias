from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.financeiro.models import MovimentacaoFinanceira
from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos


class MovimentacaoFinanceiraEstruturaTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="financeiro47",
            password="teste123",
        )

        self.empresa_a = Empresa.objects.create(
            nome="OSC Financeiro A",
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC Financeiro B",
        )

        self.termo_a = Termos.objects.create(
            empresa=self.empresa_a,
            numtermo="FIN-A/2026",
            termo="Termo Financeiro A",
        )

        self.termo_b = Termos.objects.create(
            empresa=self.empresa_b,
            numtermo="FIN-B/2026",
            termo="Termo Financeiro B",
        )

        self.prestacao_a = Prestacao.objects.create(
            empresa=self.empresa_a,
            termo=self.termo_a,
            tipo="MENSAL",
            numtermo="FIN-A/2026",
        )

        self.prestacao_b = Prestacao.objects.create(
            empresa=self.empresa_b,
            termo=self.termo_b,
            tipo="MENSAL",
            numtermo="FIN-B/2026",
        )

        self.competencia_a = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao_a,
                ano=2026,
                mes=9,
                data_inicial=date(2026, 9, 1),
                data_final=date(2026, 9, 30),
            )
        )

        self.competencia_b = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao_b,
                ano=2026,
                mes=9,
                data_inicial=date(2026, 9, 1),
                data_final=date(2026, 9, 30),
            )
        )

    def criar_movimentacao(self, **kwargs):
        dados = {
            "empresa": self.empresa_a,
            "termo": self.termo_a,
            "prestacao": self.prestacao_a,
            "competencia": self.competencia_a,
            "data": date(2026, 9, 8),
            "tipo": (
                MovimentacaoFinanceira.Tipo.REPASSE
            ),
            "valor": Decimal("1000.00"),
            "descricao": "Repasse de teste",
            "criado_por": self.usuario,
        }

        dados.update(kwargs)

        return MovimentacaoFinanceira(**dados)

    def test_movimentacao_valida_e_aceita(self):
        movimento = self.criar_movimentacao()

        movimento.full_clean()
        movimento.save()

        self.assertEqual(
            MovimentacaoFinanceira.objects.count(),
            1,
        )

    def test_valor_negativo_e_rejeitado(self):
        movimento = self.criar_movimentacao(
            valor=Decimal("-1.00"),
        )

        with self.assertRaises(ValidationError):
            movimento.full_clean()

    def test_valor_zero_e_rejeitado(self):
        movimento = self.criar_movimentacao(
            valor=Decimal("0.00"),
        )

        with self.assertRaises(ValidationError):
            movimento.full_clean()

    def test_termo_de_outra_empresa_e_rejeitado(self):
        movimento = self.criar_movimentacao(
            termo=self.termo_b,
        )

        with self.assertRaises(ValidationError) as contexto:
            movimento.full_clean()

        self.assertIn(
            "termo",
            contexto.exception.message_dict,
        )

    def test_prestacao_de_outro_termo_e_rejeitada(self):
        movimento = self.criar_movimentacao(
            prestacao=self.prestacao_b,
            competencia=None,
        )

        with self.assertRaises(ValidationError) as contexto:
            movimento.full_clean()

        self.assertIn(
            "prestacao",
            contexto.exception.message_dict,
        )

    def test_competencia_de_outra_prestacao_e_rejeitada(self):
        movimento = self.criar_movimentacao(
            competencia=self.competencia_b,
        )

        with self.assertRaises(ValidationError) as contexto:
            movimento.full_clean()

        self.assertIn(
            "competencia",
            contexto.exception.message_dict,
        )

    def test_prestacao_e_competencia_sao_opcionais(self):
        movimento = self.criar_movimentacao(
            prestacao=None,
            competencia=None,
        )

        movimento.full_clean()
        movimento.save()

        self.assertIsNone(
            movimento.prestacao,
        )
        self.assertIsNone(
            movimento.competencia,
        )

    def test_movimentacoes_de_empresas_ficam_isoladas(self):
        movimento_a = self.criar_movimentacao(
            valor=Decimal("100.00"),
        )
        movimento_a.full_clean()
        movimento_a.save()

        movimento_b = self.criar_movimentacao(
            empresa=self.empresa_b,
            termo=self.termo_b,
            prestacao=self.prestacao_b,
            competencia=self.competencia_b,
            valor=Decimal("900.00"),
        )
        movimento_b.full_clean()
        movimento_b.save()

        movimentos_a = (
            MovimentacaoFinanceira.objects.filter(
                empresa=self.empresa_a,
            )
        )

        movimentos_b = (
            MovimentacaoFinanceira.objects.filter(
                empresa=self.empresa_b,
            )
        )

        self.assertEqual(
            movimentos_a.count(),
            1,
        )
        self.assertEqual(
            movimentos_b.count(),
            1,
        )

        self.assertEqual(
            movimentos_a.get().valor,
            Decimal("100.00"),
        )
        self.assertEqual(
            movimentos_b.get().valor,
            Decimal("900.00"),
        )

    def test_saldos_financeiros_por_tipo(self):
        dados = [
            (
                MovimentacaoFinanceira.Tipo.REPASSE,
                "1000.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.DEPOSITO_OSC,
                "100.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.RENDIMENTO,
                "50.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.CREDITO_AUTORIZADO,
                "25.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.RESGATE_AUTOMATICO,
                "200.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.ESTORNO,
                "10.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.APLICACAO,
                "500.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
                "30.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.DESPESA_BANCARIA,
                "5.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.IMPOSTO_RENDA,
                "15.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.IOF,
                "2.00",
            ),
        ]

        for tipo, valor in dados:
            movimento = self.criar_movimentacao(
                tipo=tipo,
                valor=Decimal(valor),
            )
            movimento.full_clean()
            movimento.save()

        self.assertEqual(
            self.empresa_a.saldoRepasse,
            Decimal("1000.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoDepositoOsc,
            Decimal("100.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoRendimento,
            Decimal("50.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoCreditoAutorizado,
            Decimal("25.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoResgateAutomatico,
            Decimal("200.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoEstorno,
            Decimal("10.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoAplicacao,
            Decimal("500.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoDebitoAutorizado,
            Decimal("30.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoDespesaBancaria,
            Decimal("5.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoImpostoRenda,
            Decimal("15.00"),
        )
        self.assertEqual(
            self.empresa_a.saldoIof,
            Decimal("2.00"),
        )

    def test_receita_total(self):
        for tipo, valor in [
            (
                MovimentacaoFinanceira.Tipo.REPASSE,
                "1000.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.DEPOSITO_OSC,
                "100.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.RENDIMENTO,
                "50.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.CREDITO_AUTORIZADO,
                "25.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.ESTORNO,
                "10.00",
            ),
        ]:
            movimento = self.criar_movimentacao(
                tipo=tipo,
                valor=Decimal(valor),
            )
            movimento.full_clean()
            movimento.save()

        self.assertEqual(
            self.empresa_a.receitaTotal,
            Decimal("1185.00"),
        )

    def test_saldo_conta_aplicacao(self):
        for tipo, valor in [
            (
                MovimentacaoFinanceira.Tipo.APLICACAO,
                "1000.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.RESGATE_AUTOMATICO,
                "250.00",
            ),
        ]:
            movimento = self.criar_movimentacao(
                tipo=tipo,
                valor=Decimal(valor),
            )
            movimento.full_clean()
            movimento.save()

        self.assertEqual(
            self.empresa_a.saldoContaAplicacao,
            Decimal("750.00"),
        )

    def test_prestacao_de_outra_empresa_e_rejeitada(self):
        prestacao_inconsistente = Prestacao.objects.create(
            empresa=self.empresa_b,
            termo=self.termo_a,
            tipo="MENSAL",
            numtermo="FIN-INCONSISTENTE/2026",
        )

        movimento = self.criar_movimentacao(
            empresa=self.empresa_a,
            termo=self.termo_a,
            prestacao=prestacao_inconsistente,
            competencia=None,
        )

        with self.assertRaises(ValidationError) as contexto:
            movimento.full_clean()

        self.assertIn(
            "prestacao",
            contexto.exception.message_dict,
        )

        self.assertIn(
            "empresa selecionada",
            contexto.exception.message_dict["prestacao"][0],
        )

    def test_receita_total_nao_inclui_resgate_automatico(self):
        for tipo, valor in [
            (
                MovimentacaoFinanceira.Tipo.REPASSE,
                "1000.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.RESGATE_AUTOMATICO,
                "250.00",
            ),
        ]:
            movimento = self.criar_movimentacao(
                tipo=tipo,
                valor=Decimal(valor),
            )
            movimento.full_clean()
            movimento.save()

        self.assertEqual(
            self.empresa_a.receitaTotal,
            Decimal("1000.00"),
        )

    def test_despesa_total(self):
        for tipo, valor in [
            (
                MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
                "30.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.DESPESA_BANCARIA,
                "5.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.IMPOSTO_RENDA,
                "15.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.IOF,
                "2.00",
            ),
        ]:
            movimento = self.criar_movimentacao(
                tipo=tipo,
                valor=Decimal(valor),
            )
            movimento.full_clean()
            movimento.save()

        self.assertEqual(
            self.empresa_a.despesaTotal,
            Decimal("52.00"),
        )

    def test_saldo_financeiro(self):
        dados = [
            (
                MovimentacaoFinanceira.Tipo.REPASSE,
                "1000.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.DEPOSITO_OSC,
                "100.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.RENDIMENTO,
                "50.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.CREDITO_AUTORIZADO,
                "25.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.RESGATE_AUTOMATICO,
                "200.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.ESTORNO,
                "10.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.APLICACAO,
                "500.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
                "30.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.DESPESA_BANCARIA,
                "5.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.IMPOSTO_RENDA,
                "15.00",
            ),
            (
                MovimentacaoFinanceira.Tipo.IOF,
                "2.00",
            ),
        ]

        for tipo, valor in dados:
            movimento = self.criar_movimentacao(
                tipo=tipo,
                valor=Decimal(valor),
            )
            movimento.full_clean()
            movimento.save()

        self.assertEqual(
            self.empresa_a.saldoFinanceiro,
            Decimal("833.00"),
        )

    def test_saldos_nao_misturam_empresas(self):
        movimento_a = self.criar_movimentacao(
            tipo=MovimentacaoFinanceira.Tipo.REPASSE,
            valor=Decimal("100.00"),
        )
        movimento_a.full_clean()
        movimento_a.save()

        movimento_b = self.criar_movimentacao(
            empresa=self.empresa_b,
            termo=self.termo_b,
            prestacao=self.prestacao_b,
            competencia=self.competencia_b,
            tipo=MovimentacaoFinanceira.Tipo.REPASSE,
            valor=Decimal("900.00"),
        )
        movimento_b.full_clean()
        movimento_b.save()

        self.assertEqual(
            self.empresa_a.saldoRepasse,
            Decimal("100.00"),
        )
        self.assertEqual(
            self.empresa_b.saldoRepasse,
            Decimal("900.00"),
        )
