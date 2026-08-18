from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)
from apps.planos_trabalho.temporal import (
    resumo_temporal_item,
)
from apps.planos_trabalho.vinculos import (
    vincular_lancamento_item,
)
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PlanoTrabalhoSprint457Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.7"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT457/26",
            termo="Termo Sprint 45.7",
        )

        self.plano = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano Sprint 45.7",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.item = ItemPlanoTrabalho.objects.create(
            plano=self.plano,
            codigo="TEMP-457",
            descricao="Item temporal",
            valor_total_previsto=Decimal("10000.00"),
            inicio_execucao=date(2026, 4, 1),
            fim_execucao=date(2026, 9, 30),
        )

    def criar_lancamento(
        self,
        numero,
        data_documento,
        data_pagamento=None,
    ):
        return Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento=numero,
            tipo_documento=(
                Lancamento.TipoDocumento.NFE
            ),
            numero_documento=numero,
            data_documento=data_documento,
            data_pagamento=data_pagamento,
            descricao="Execução temporal",
            valor_documento=Decimal("100.00"),
        )

    def test_execucao_dentro_periodo_e_compativel(self):
        lancamento = self.criar_lancamento(
            "457-001",
            date(2026, 6, 15),
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        resultado = (
            motor_regras
            .analisar_execucao_temporal_item(
                self.item
            )
        )

        self.assertIn(
            "PT_EXEC_PERIODO_COMPATIVEL",
            {
                item.codigo
                for item in resultado.achados
            },
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "sem_inconsistencia_relevante_detectada",
        )

    def test_execucao_anterior_gera_alerta(self):
        lancamento = self.criar_lancamento(
            "457-002",
            date(2026, 3, 20),
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        resultado = (
            motor_regras
            .analisar_execucao_temporal_item(
                self.item
            )
        )

        self.assertIn(
            "PT_EXEC_ANTES_PERIODO_PREVISTO",
            {
                item.codigo
                for item in resultado.achados
            },
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "requer_conferencia",
        )

    def test_execucao_posterior_gera_alerta(self):
        lancamento = self.criar_lancamento(
            "457-003",
            date(2026, 10, 10),
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        resultado = (
            motor_regras
            .analisar_execucao_temporal_item(
                self.item
            )
        )

        self.assertIn(
            "PT_EXEC_APOS_PERIODO_PREVISTO",
            {
                item.codigo
                for item in resultado.achados
            },
        )

    def test_data_documento_tem_prioridade_sobre_pagamento(self):
        lancamento = self.criar_lancamento(
            "457-004",
            date(2026, 9, 20),
            date(2026, 10, 15),
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        resumo = resumo_temporal_item(
            self.item
        )

        execucao = resumo.execucoes[0]

        self.assertEqual(
            execucao.data_referencia,
            date(2026, 9, 20),
        )

        self.assertEqual(
            execucao.origem_data,
            "documento",
        )

        self.assertEqual(
            execucao.situacao_temporal,
            "dentro",
        )

    def test_item_sem_periodo_gera_informativo(self):
        self.item.inicio_execucao = None
        self.item.fim_execucao = None

        self.item.save(
            update_fields=[
                "inicio_execucao",
                "fim_execucao",
            ]
        )

        resultado = (
            motor_regras
            .analisar_execucao_temporal_item(
                self.item
            )
        )

        self.assertIn(
            "PT_ITEM_SEM_PERIODO_PREVISTO",
            {
                item.codigo
                for item in resultado.achados
            },
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "sem_inconsistencia_relevante_detectada",
        )

    def test_analise_temporal_nao_aplica_glosa(self):
        lancamento = self.criar_lancamento(
            "457-005",
            date(2026, 10, 10),
        )

        vincular_lancamento_item(
            lancamento,
            self.item,
        )

        situacao_antes = lancamento.situacao
        tipo_glosa_antes = lancamento.tipo_glosa
        valor_glosa_antes = lancamento.valor_glosa

        motor_regras.analisar_execucao_temporal_item(
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
