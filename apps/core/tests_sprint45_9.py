from datetime import date
from decimal import Decimal

from django.db import models
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.metas.models import MetaExecucao
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)
from apps.planos_trabalho.vinculos import (
    vincular_lancamento_item,
)
from apps.prestacao.models import Prestacao
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PlanoTrabalhoSprint459Tests(TestCase):

    def criar_prestacao(
        self,
        *,
        empresa,
        numtermo,
    ):
        kwargs = {
            "empresa": empresa,
            "numtermo": numtermo,
        }

        for campo in Prestacao._meta.fields:
            if (
                campo.primary_key
                or campo.name in kwargs
            ):
                continue

            if campo.has_default():
                continue

            if campo.null:
                continue

            if isinstance(
                campo,
                models.ForeignKey,
            ):
                continue

            if isinstance(
                campo,
                (
                    models.CharField,
                    models.TextField,
                    models.FileField,
                ),
            ):
                kwargs[campo.name] = ""

            elif isinstance(
                campo,
                models.BooleanField,
            ):
                kwargs[campo.name] = False

            elif isinstance(
                campo,
                models.IntegerField,
            ):
                kwargs[campo.name] = 0

            elif isinstance(
                campo,
                models.FloatField,
            ):
                kwargs[campo.name] = 0.0

            elif isinstance(
                campo,
                models.DecimalField,
            ):
                kwargs[campo.name] = Decimal("0")

            elif isinstance(
                campo,
                models.DateField,
            ):
                kwargs[campo.name] = date(
                    2026,
                    1,
                    1,
                )

        return Prestacao.objects.create(
            **kwargs
        )

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.9"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT459/26",
            termo="Termo Sprint 45.9",
            objeto=(
                "Atendimento socioassistencial "
                "a famílias em vulnerabilidade"
            ),
        )

        self.prestacao = self.criar_prestacao(
            empresa=self.empresa,
            numtermo="PT459/26",
        )

        self.meta = MetaExecucao.objects.create(
            prestacao=self.prestacao,
            codigo="META-459",
            titulo="Atendimento às famílias",
            descricao=(
                "Atendimento socioassistencial "
                "às famílias"
            ),
            unidade="numero",
            valor_previsto=Decimal("100.00"),
            valor_realizado=Decimal("20.00"),
            inicio=date(2026, 1, 1),
            fim=date(2026, 12, 31),
        )

        self.plano = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano Sprint 45.9",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.item = ItemPlanoTrabalho.objects.create(
            plano=self.plano,
            codigo="ITEM-459",
            rubrica_nivel_1="Custeio",
            descricao=(
                "Material para atendimento "
                "das famílias"
            ),
            unidade="unidade",
            quantidade_prevista=Decimal("10.0000"),
            valor_unitario_previsto=Decimal("100.00"),
            valor_total_previsto=Decimal("1000.00"),
            inicio_execucao=date(2026, 1, 1),
            fim_execucao=date(2026, 12, 31),
            meta=self.meta,
        )

    def criar_lancamento(
        self,
        numero,
        valor,
        *,
        data_documento=date(2026, 5, 10),
        quantidade=Decimal("1.0000"),
        valor_unitario=None,
    ):
        lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento=numero,
            tipo_documento=(
                Lancamento.TipoDocumento.NFE
            ),
            numero_documento=numero,
            data_documento=data_documento,
            data_pagamento=date(2026, 5, 15),
            descricao=(
                "Material para atendimento "
                "das famílias"
            ),
            valor_documento=Decimal(valor),
        )

        if valor_unitario is None:
            valor_unitario = Decimal(valor)

        vincular_lancamento_item(
            lancamento,
            self.item,
            quantidade_executada=quantidade,
            valor_unitario_executado=(
                valor_unitario
            ),
        )

        return lancamento

    def test_consolida_quatro_dimensoes(self):
        self.criar_lancamento(
            "459-001",
            "100.00",
            quantidade=Decimal("1.0000"),
            valor_unitario=Decimal("100.00"),
        )

        resultado = (
            motor_regras
            .analisar_item_plano_completo(
                self.item
            )
        )

        self.assertIsNotNone(
            resultado.financeiro
        )

        self.assertIsNotNone(
            resultado.quantitativo
        )

        self.assertIsNotNone(
            resultado.temporal
        )

        self.assertIsNotNone(
            resultado.meta_objeto
        )

    def test_resumo_executivo_contem_saldos(self):
        self.criar_lancamento(
            "459-002",
            "300.00",
            quantidade=Decimal("3.0000"),
            valor_unitario=Decimal("100.00"),
        )

        resultado = (
            motor_regras
            .analisar_item_plano_completo(
                self.item
            )
        )

        resumo = resultado.resumo_executivo

        self.assertEqual(
            resumo["financeiro"]["valor_previsto"],
            Decimal("1000.00"),
        )

        self.assertEqual(
            resumo["financeiro"]["valor_executado"],
            Decimal("300.00"),
        )

        self.assertEqual(
            resumo["financeiro"]["saldo"],
            Decimal("700.00"),
        )

    def test_criticos_ficam_antes_dos_alertas(self):
        self.criar_lancamento(
            "459-003",
            "1200.00",
            quantidade=Decimal("12.0000"),
            valor_unitario=Decimal("100.00"),
        )

        resultado = (
            motor_regras
            .analisar_item_plano_completo(
                self.item
            )
        )

        severidades = [
            achado.severidade
            for achado
            in resultado.achados
        ]

        if (
            "critico" in severidades
            and "alerta" in severidades
        ):
            self.assertLess(
                severidades.index("critico"),
                severidades.index("alerta"),
            )

        self.assertTrue(
            resultado.criticos
        )

    def test_resultado_critico_gera_conclusao_executiva(self):
        self.criar_lancamento(
            "459-004",
            "1200.00",
            quantidade=Decimal("12.0000"),
            valor_unitario=Decimal("100.00"),
        )

        resultado = (
            motor_regras
            .analisar_item_plano_completo(
                self.item
            )
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

        self.assertIn(
            "pendências críticas",
            resultado.conclusao_executiva,
        )

        self.assertIn(
            "Nenhuma glosa",
            resultado.conclusao_executiva,
        )

    def test_alerta_sem_critico_requer_conferencia(self):
        self.criar_lancamento(
            "459-005",
            "105.00",
            quantidade=Decimal("1.0000"),
            valor_unitario=Decimal("105.00"),
        )

        resultado = (
            motor_regras
            .analisar_item_plano_completo(
                self.item
            )
        )

        self.assertFalse(
            resultado.criticos
        )

        self.assertTrue(
            resultado.alertas
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "requer_conferencia",
        )

    def test_analise_consolidada_nao_aplica_glosa(self):
        lancamento = self.criar_lancamento(
            "459-006",
            "1200.00",
            quantidade=Decimal("12.0000"),
            valor_unitario=Decimal("100.00"),
        )

        situacao_antes = (
            lancamento.situacao
        )

        tipo_glosa_antes = (
            lancamento.tipo_glosa
        )

        valor_glosa_antes = (
            lancamento.valor_glosa
        )

        motor_regras.analisar_item_plano_completo(
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
