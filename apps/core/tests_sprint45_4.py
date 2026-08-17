from datetime import date
from decimal import Decimal

from django.db import (
    IntegrityError,
    transaction,
)
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
    VinculoLancamentoItemPlano,
)
from apps.planos_trabalho.services import (
    ativar_versao,
)
from apps.planos_trabalho.vinculos import (
    validar_item_para_lancamento,
    vincular_lancamento_item,
    vinculo_ativo_lancamento,
)
from apps.termos.models import Termos


class PlanoTrabalhoSprint454Tests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.4"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT454/26",
            termo="Termo Sprint 45.4",
        )

        self.plano_1 = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano inicial",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.item_1 = (
            ItemPlanoTrabalho.objects.create(
                plano=self.plano_1,
                codigo="MAT-001",
                rubrica_nivel_1="Material",
                descricao="Material de expediente",
                valor_total_previsto=Decimal(
                    "10000.00"
                ),
            )
        )

        self.lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento="PT454-001",
            tipo_documento=(
                Lancamento.TipoDocumento.NFE
            ),
            numero_documento="NF-454",
            data_documento=date(2026, 5, 10),
            data_pagamento=date(2026, 5, 15),
            descricao="Material de expediente",
            valor_documento=Decimal("500.00"),
        )

    def test_cria_vinculo_valido(self):

        vinculo = vincular_lancamento_item(
            self.lancamento,
            self.item_1,
        )

        self.assertTrue(
            vinculo.ativo
        )

        self.assertEqual(
            vinculo.item_plano,
            self.item_1,
        )

    def test_nao_permite_item_de_outro_termo(self):

        outro_termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="OUTRO454/26",
            termo="Outro Termo",
        )

        outro_plano = (
            PlanoTrabalho.objects.create(
                termo=outro_termo,
                versao=1,
                origem=PlanoTrabalho.Origem.INICIAL,
                situacao=(
                    PlanoTrabalho.Situacao.VIGENTE
                ),
                inicio_vigencia=date(2026, 1, 1),
                fim_vigencia=date(2026, 12, 31),
                data_eficacia=date(2026, 1, 1),
            )
        )

        outro_item = (
            ItemPlanoTrabalho.objects.create(
                plano=outro_plano,
                codigo="OUTRO-001",
                descricao="Outro item",
                valor_total_previsto=Decimal(
                    "1000.00"
                ),
            )
        )

        with self.assertRaises(
            ValidationError
        ):
            validar_item_para_lancamento(
                self.lancamento,
                outro_item,
            )

    def test_versao_historica_e_respeitada(self):

        plano_2 = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=2,
            titulo="Plano alterado",
            versao_anterior=self.plano_1,
            origem=(
                PlanoTrabalho
                .Origem
                .REMANEJAMENTO
            ),
            situacao=(
                PlanoTrabalho
                .Situacao
                .RASCUNHO
            ),
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 7, 1),
        )

        item_2 = ItemPlanoTrabalho.objects.create(
            plano=plano_2,
            codigo="MAT-002",
            descricao="Material remanejado",
            valor_total_previsto=Decimal(
                "15000.00"
            ),
        )

        ativar_versao(
            plano_2
        )

        # lançamento é de maio/2026,
        # portanto ainda pertence ao Plano v1
        with self.assertRaises(
            ValidationError
        ):
            validar_item_para_lancamento(
                self.lancamento,
                item_2,
            )

        plano = validar_item_para_lancamento(
            self.lancamento,
            self.item_1,
        )

        self.assertEqual(
            plano.pk,
            self.plano_1.pk,
        )

    def test_apenas_um_vinculo_ativo_por_lancamento(self):

        VinculoLancamentoItemPlano.objects.create(
            lancamento=self.lancamento,
            item_plano=self.item_1,
            ativo=True,
        )

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():

                VinculoLancamentoItemPlano.objects.create(
                    lancamento=self.lancamento,
                    item_plano=self.item_1,
                    ativo=True,
                )

    def test_novo_vinculo_desativa_anterior(self):

        primeiro = vincular_lancamento_item(
            self.lancamento,
            self.item_1,
            justificativa="Primeiro vínculo",
        )

        segundo = vincular_lancamento_item(
            self.lancamento,
            self.item_1,
            justificativa="Vínculo revisado",
        )

        primeiro.refresh_from_db()

        self.assertFalse(
            primeiro.ativo
        )

        self.assertTrue(
            segundo.ativo
        )

        self.assertEqual(
            vinculo_ativo_lancamento(
                self.lancamento
            ).pk,
            segundo.pk,
        )

    def test_nao_altera_decisao_do_lancamento(self):

        situacao_antes = (
            self.lancamento.situacao
        )

        tipo_glosa_antes = (
            self.lancamento.tipo_glosa
        )

        valor_glosa_antes = (
            self.lancamento.valor_glosa
        )

        vincular_lancamento_item(
            self.lancamento,
            self.item_1,
        )

        self.lancamento.refresh_from_db()

        self.assertEqual(
            self.lancamento.situacao,
            situacao_antes,
        )

        self.assertEqual(
            self.lancamento.tipo_glosa,
            tipo_glosa_antes,
        )

        self.assertEqual(
            self.lancamento.valor_glosa,
            valor_glosa_antes,
        )

