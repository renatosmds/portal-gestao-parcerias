from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.planos_trabalho.financeiro import (
    resumo_financeiro_item,
)
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)
from apps.planos_trabalho.vinculos import (
    vincular_lancamento_item,
)
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PlanoTrabalhoSprint455Tests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.5"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT455/26",
            termo="Termo Sprint 45.5",
        )

        self.plano = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano Sprint 45.5",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.item = ItemPlanoTrabalho.objects.create(
            plano=self.plano,
            codigo="MAT-455",
            descricao="Material de consumo",
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
            tipo_documento=(
                Lancamento.TipoDocumento.NFE
            ),
            numero_documento=numero,
            data_documento=date(2026, 5, 10),
            data_pagamento=date(2026, 5, 15),
            descricao="Material de consumo",
            valor_documento=Decimal(valor),
        )

    def test_calcula_valor_executado_e_saldo(self):

        lancamento = self.criar_lancamento(
            "455-001",
            "300.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        resumo = resumo_financeiro_item(
            self.item
        )

        self.assertEqual(
            resumo.valor_previsto,
            Decimal("1000.00"),
        )

        self.assertEqual(
            resumo.valor_executado,
            Decimal("300.00"),
        )

        self.assertEqual(
            resumo.saldo,
            Decimal("700.00"),
        )

    def test_soma_multiplos_lancamentos(self):

        lancamento_1 = self.criar_lancamento(
            "455-002",
            "300.00",
        )

        lancamento_2 = self.criar_lancamento(
            "455-003",
            "250.00",
        )

        vincular_lancamento_item(
            lancamento_1,
            self.item,
        )

        vincular_lancamento_item(
            lancamento_2,
            self.item,
        )

        resumo = resumo_financeiro_item(
            self.item
        )

        self.assertEqual(
            resumo.valor_executado,
            Decimal("550.00"),
        )

        self.assertEqual(
            resumo.saldo,
            Decimal("450.00"),
        )

    def test_execucao_superior_gera_critico(self):

        lancamento = self.criar_lancamento(
            "455-004",
            "1200.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        resultado = (
            motor_regras
            .analisar_execucao_item_plano(
                self.item
            )
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "PT_ITEM_VALOR_EXCEDIDO",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_execucao_parcial_e_informativa(self):

        lancamento = self.criar_lancamento(
            "455-005",
            "400.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        resultado = (
            motor_regras
            .analisar_execucao_item_plano(
                self.item
            )
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "PT_ITEM_EXECUCAO_PARCIAL",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "sem_inconsistencia_relevante_detectada",
        )

    def test_execucao_total_identifica_saldo_zero(self):

        lancamento = self.criar_lancamento(
            "455-006",
            "1000.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        resultado = (
            motor_regras
            .analisar_execucao_item_plano(
                self.item
            )
        )

        self.assertEqual(
            resultado.resumo.saldo,
            Decimal("0.00"),
        )

        self.assertIn(
            "PT_ITEM_TOTALMENTE_EXECUTADO",
            {
                item.codigo
                for item in resultado.achados
            },
        )

    def test_analise_nao_aplica_glosa(self):

        lancamento = self.criar_lancamento(
            "455-007",
            "1200.00",
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        situacao_antes = lancamento.situacao
        tipo_glosa_antes = lancamento.tipo_glosa
        valor_glosa_antes = lancamento.valor_glosa

        motor_regras.analisar_execucao_item_plano(
            self.item
        )

        lancamento.refresh_from_db()

        self.assertEqual(
            lancamento.situacao,
            situacao_antes,
        )

        self.assertEqual(
            lancamento.tipo_glosa,
            tipo_glosa_antes,
        )

        self.assertEqual(
            lancamento.valor_glosa,
            valor_glosa_antes,
        )
