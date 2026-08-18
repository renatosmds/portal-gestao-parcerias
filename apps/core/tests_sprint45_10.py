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


class PlanoTrabalhoSprint4510Tests(TestCase):

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
            nome="OSC Sprint 45.10"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT4510/26",
            termo="Termo Sprint 45.10",
            objeto=(
                "Atendimento socioassistencial "
                "a famílias em vulnerabilidade"
            ),
        )

        self.prestacao = self.criar_prestacao(
            empresa=self.empresa,
            numtermo="PT4510/26",
        )

        self.meta = MetaExecucao.objects.create(
            prestacao=self.prestacao,
            codigo="META-4510",
            titulo="Atendimento às famílias",
            descricao=(
                "Realizar atendimento "
                "socioassistencial às famílias"
            ),
            unidade="numero",
            valor_previsto=Decimal("100.00"),
            valor_realizado=Decimal("25.00"),
            inicio=date(2026, 1, 1),
            fim=date(2026, 12, 31),
        )

        self.plano = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano Sprint 45.10",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.item_1 = ItemPlanoTrabalho.objects.create(
            plano=self.plano,
            codigo="ITEM-A",
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

        self.item_2 = ItemPlanoTrabalho.objects.create(
            plano=self.plano,
            codigo="ITEM-B",
            descricao=(
                "Material socioassistencial "
                "para famílias"
            ),
            unidade="unidade",
            quantidade_prevista=Decimal("20.0000"),
            valor_unitario_previsto=Decimal("100.00"),
            valor_total_previsto=Decimal("2000.00"),
            inicio_execucao=date(2026, 1, 1),
            fim_execucao=date(2026, 12, 31),
            meta=self.meta,
        )

    def criar_lancamento(
        self,
        item,
        numero,
        valor,
        quantidade,
        valor_unitario,
    ):
        lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento=numero,
            tipo_documento=(
                Lancamento.TipoDocumento.NFE
            ),
            numero_documento=numero,
            data_documento=date(2026, 5, 10),
            data_pagamento=date(2026, 5, 15),
            descricao=item.descricao,
            valor_documento=Decimal(valor),
        )

        vincular_lancamento_item(
            lancamento,
            item,
            quantidade_executada=Decimal(
                quantidade
            ),
            valor_unitario_executado=Decimal(
                valor_unitario
            ),
        )

        return lancamento

    def test_consolida_todos_os_itens_ativos(self):
        resultado = (
            motor_regras
            .analisar_plano_trabalho_completo(
                self.plano
            )
        )

        self.assertEqual(
            resultado.quantidade_itens,
            2,
        )

    def test_soma_valores_previstos_do_plano(self):
        resultado = (
            motor_regras
            .analisar_plano_trabalho_completo(
                self.plano
            )
        )

        self.assertEqual(
            resultado.valor_previsto,
            Decimal("3000.00"),
        )

    def test_soma_execucao_e_calcula_saldo(self):
        self.criar_lancamento(
            self.item_1,
            "4510-001",
            "300.00",
            "3.0000",
            "100.00",
        )

        self.criar_lancamento(
            self.item_2,
            "4510-002",
            "500.00",
            "5.0000",
            "100.00",
        )

        resultado = (
            motor_regras
            .analisar_plano_trabalho_completo(
                self.plano
            )
        )

        self.assertEqual(
            resultado.valor_executado,
            Decimal("800.00"),
        )

        self.assertEqual(
            resultado.saldo,
            Decimal("2200.00"),
        )

    def test_item_critico_torna_plano_critico(self):
        self.criar_lancamento(
            self.item_1,
            "4510-003",
            "1200.00",
            "12.0000",
            "100.00",
        )

        resultado = (
            motor_regras
            .analisar_plano_trabalho_completo(
                self.plano
            )
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

        self.assertEqual(
            resultado.quantidade_itens_criticos,
            1,
        )

        self.assertTrue(
            resultado.criticos
        )

    def test_item_inativo_nao_entra_na_consolidacao(self):
        self.item_2.ativo = False
        self.item_2.save(
            update_fields=["ativo"]
        )

        resultado = (
            motor_regras
            .analisar_plano_trabalho_completo(
                self.plano
            )
        )

        self.assertEqual(
            resultado.quantidade_itens,
            1,
        )

        self.assertEqual(
            resultado.valor_previsto,
            Decimal("1000.00"),
        )

    def test_consolidacao_nao_aplica_glosa(self):
        lancamento = self.criar_lancamento(
            self.item_1,
            "4510-004",
            "1200.00",
            "12.0000",
            "100.00",
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

        resultado = (
            motor_regras
            .analisar_plano_trabalho_completo(
                self.plano
            )
        )

        self.assertIn(
            "pendências críticas",
            resultado.conclusao_executiva,
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
