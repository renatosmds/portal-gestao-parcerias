from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.financeiro.models import MovimentacaoFinanceira
from apps.financeiro.resumos import resumo_financeiro_competencia
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos


class ResumoFinanceiroCompetenciaTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="resumo_competencia",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Resumo Competencia",
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RES-001/2026",
            termo="Termo Resumo Competencia",
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="MENSAL",
            numtermo="RES-001/2026",
        )

        self.janeiro = CompetenciaPrestacao.objects.create(
            prestacao=self.prestacao,
            ano=2026,
            mes=1,
            data_inicial=date(2026, 1, 1),
            data_final=date(2026, 1, 31),
            saldo_inicial=Decimal("100.00"),
            saldo_final=Decimal("650.00"),
        )

        self.fevereiro = CompetenciaPrestacao.objects.create(
            prestacao=self.prestacao,
            ano=2026,
            mes=2,
            data_inicial=date(2026, 2, 1),
            data_final=date(2026, 2, 28),
            saldo_inicial=Decimal("650.00"),
            saldo_final=Decimal("850.00"),
        )

    def criar_movimento(
        self,
        competencia,
        tipo,
        valor,
        descricao,
    ):
        return MovimentacaoFinanceira.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=competencia,
            data=competencia.data_inicial,
            tipo=tipo,
            valor=Decimal(valor),
            descricao=descricao,
            criado_por=self.usuario,
        )

    def criar_lancamento(
        self,
        competencia,
        numero,
        valor,
    ):
        return Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=competencia,
            numero_lancamento=numero,
            data_documento=competencia.data_inicial,
            descricao=f"Despesa {numero}",
            valor_documento=Decimal(valor),
            criado_por=self.usuario,
        )

    def test_competencias_nao_misturam_movimentacoes(self):
        self.criar_movimento(
            self.janeiro,
            MovimentacaoFinanceira.Tipo.REPASSE,
            "1000.00",
            "Repasse janeiro",
        )

        self.criar_movimento(
            self.fevereiro,
            MovimentacaoFinanceira.Tipo.REPASSE,
            "300.00",
            "Repasse fevereiro",
        )

        janeiro = resumo_financeiro_competencia(
            self.janeiro
        )

        fevereiro = resumo_financeiro_competencia(
            self.fevereiro
        )

        self.assertEqual(
            janeiro["repasse"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            fevereiro["repasse"],
            Decimal("300.00"),
        )

    def test_competencias_nao_misturam_lancamentos(self):
        self.criar_lancamento(
            self.janeiro,
            "JAN-001",
            "250.00",
        )

        self.criar_lancamento(
            self.fevereiro,
            "FEV-001",
            "100.00",
        )

        janeiro = resumo_financeiro_competencia(
            self.janeiro
        )

        fevereiro = resumo_financeiro_competencia(
            self.fevereiro
        )

        self.assertEqual(
            janeiro["valor_lancamentos"],
            Decimal("250.00"),
        )

        self.assertEqual(
            fevereiro["valor_lancamentos"],
            Decimal("100.00"),
        )

    def test_saldo_final_calculado_e_diferenca(self):
        self.criar_movimento(
            self.janeiro,
            MovimentacaoFinanceira.Tipo.REPASSE,
            "1000.00",
            "Repasse janeiro",
        )

        self.criar_movimento(
            self.janeiro,
            MovimentacaoFinanceira.Tipo.RENDIMENTO,
            "20.00",
            "Rendimento janeiro",
        )

        self.criar_movimento(
            self.janeiro,
            MovimentacaoFinanceira.Tipo.APLICACAO,
            "100.00",
            "Aplicacao janeiro",
        )

        self.criar_movimento(
            self.janeiro,
            MovimentacaoFinanceira.Tipo.DESPESA_BANCARIA,
            "20.00",
            "Tarifa janeiro",
        )

        self.criar_lancamento(
            self.janeiro,
            "JAN-002",
            "350.00",
        )

        resumo = resumo_financeiro_competencia(
            self.janeiro
        )

        self.assertEqual(
            resumo["receita_total"],
            Decimal("1020.00"),
        )

        self.assertEqual(
            resumo["despesa_total"],
            Decimal("370.00"),
        )

        self.assertEqual(
            resumo["total_entradas"],
            Decimal("1020.00"),
        )

        self.assertEqual(
            resumo["total_saidas"],
            Decimal("470.00"),
        )

        self.assertEqual(
            resumo["movimento_financeiro"],
            Decimal("550.00"),
        )

        self.assertEqual(
            resumo["saldo_final_calculado"],
            Decimal("650.00"),
        )

        self.assertEqual(
            resumo["diferenca_saldo"],
            Decimal("0.00"),
        )

    def test_diferenca_aponta_divergencia_de_saldo(self):
        self.criar_movimento(
            self.fevereiro,
            MovimentacaoFinanceira.Tipo.REPASSE,
            "300.00",
            "Repasse fevereiro",
        )

        self.criar_lancamento(
            self.fevereiro,
            "FEV-002",
            "50.00",
        )

        resumo = resumo_financeiro_competencia(
            self.fevereiro
        )

        self.assertEqual(
            resumo["saldo_final_calculado"],
            Decimal("900.00"),
        )

        self.assertEqual(
            resumo["saldo_final_informado"],
            Decimal("850.00"),
        )

        self.assertEqual(
            resumo["diferenca_saldo"],
            Decimal("-50.00"),
        )
