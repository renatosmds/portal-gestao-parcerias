from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)
from apps.planos_trabalho.quantitativo import (
    resumo_quantitativo_item,
)
from apps.planos_trabalho.vinculos import (
    vincular_lancamento_item,
)
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PlanoTrabalhoSprint456Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.6"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT456/26",
            termo="Termo Sprint 45.6",
        )

        self.plano = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano Sprint 45.6",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.item = ItemPlanoTrabalho.objects.create(
            plano=self.plano,
            codigo="MAT-456",
            descricao="Material",
            unidade="unidade",
            quantidade_prevista=Decimal("10.0000"),
            valor_unitario_previsto=Decimal("100.00"),
            valor_total_previsto=Decimal("1000.00"),
        )

    def criar_lancamento(
        self,
        numero,
        valor,
    ):
        return Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento=numero,
            tipo_documento=Lancamento.TipoDocumento.NFE,
            numero_documento=numero,
            data_documento=date(2026, 5, 10),
            data_pagamento=date(2026, 5, 15),
            descricao="Material",
            valor_documento=Decimal(valor),
        )

    def test_soma_quantidades_executadas(self):
        l1 = self.criar_lancamento(
            "456-001",
            "200.00",
        )

        l2 = self.criar_lancamento(
            "456-002",
            "300.00",
        )

        vincular_lancamento_item(
            l1,
            self.item,
            quantidade_executada=Decimal("2.0000"),
            valor_unitario_executado=Decimal("100.00"),
        )

        vincular_lancamento_item(
            l2,
            self.item,
            quantidade_executada=Decimal("3.0000"),
            valor_unitario_executado=Decimal("100.00"),
        )

        resumo = resumo_quantitativo_item(
            self.item
        )

        self.assertEqual(
            resumo.quantidade_executada,
            Decimal("5.0000"),
        )

        self.assertEqual(
            resumo.saldo_quantidade,
            Decimal("5.0000"),
        )

    def test_quantidade_superior_gera_critico(self):
        lancamento = self.criar_lancamento(
            "456-003",
            "1100.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
            quantidade_executada=Decimal("11.0000"),
            valor_unitario_executado=Decimal("100.00"),
        )

        resultado = (
            motor_regras
            .analisar_execucao_quantitativa_item(
                self.item
            )
        )

        self.assertIn(
            "PT_EXEC_QUANTIDADE_SUPERIOR_PREVISTA",
            {
                item.codigo
                for item in resultado.achados
            },
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_valor_unitario_superior_gera_alerta(self):
        lancamento = self.criar_lancamento(
            "456-004",
            "315.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
            quantidade_executada=Decimal("3.0000"),
            valor_unitario_executado=Decimal("105.00"),
        )

        resultado = (
            motor_regras
            .analisar_execucao_quantitativa_item(
                self.item
            )
        )

        self.assertIn(
            "PT_EXEC_VALOR_UNITARIO_SUPERIOR_PREVISTO",
            {
                item.codigo
                for item in resultado.achados
            },
        )

    def test_quantidade_ausente_gera_alerta(self):
        lancamento = self.criar_lancamento(
            "456-005",
            "200.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
            valor_unitario_executado=Decimal("100.00"),
        )

        resultado = (
            motor_regras
            .analisar_execucao_quantitativa_item(
                self.item
            )
        )

        self.assertIn(
            "PT_EXEC_QUANTIDADE_NAO_INFORMADA",
            {
                item.codigo
                for item in resultado.achados
            },
        )

    def test_total_calculado_divergente_gera_alerta(self):
        lancamento = self.criar_lancamento(
            "456-006",
            "250.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
            quantidade_executada=Decimal("2.0000"),
            valor_unitario_executado=Decimal("100.00"),
        )

        resultado = (
            motor_regras
            .analisar_execucao_quantitativa_item(
                self.item
            )
        )

        self.assertIn(
            "PT_EXEC_TOTAL_CALCULADO_DIVERGE_DOCUMENTO",
            {
                item.codigo
                for item in resultado.achados
            },
        )

    def test_analise_quantitativa_nao_aplica_glosa(self):
        lancamento = self.criar_lancamento(
            "456-007",
            "1100.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
            quantidade_executada=Decimal("11.0000"),
            valor_unitario_executado=Decimal("100.00"),
        )

        situacao_antes = lancamento.situacao
        valor_glosa_antes = lancamento.valor_glosa

        motor_regras.analisar_execucao_quantitativa_item(
            self.item
        )

        lancamento.refresh_from_db()

        self.assertEqual(
            lancamento.situacao,
            situacao_antes,
        )

        self.assertEqual(
            lancamento.valor_glosa,
            valor_glosa_antes,
        )
