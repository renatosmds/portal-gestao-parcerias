from datetime import date
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.financeiro.models import (
    ConciliacaoFinanceira,
    ImportacaoOFX,
    MovimentacaoFinanceira,
)
from apps.financeiro.servicos_ofx import importar_ofx
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos


class ImportacaoOFXAdminTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_superuser(
            username="admin_ofx",
            email="admin_ofx@example.com",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Admin OFX"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="ADM-OFX/2026",
            termo="Termo Admin OFX",
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="MENSAL",
            numtermo="ADM-OFX/2026",
        )

        self.competencia = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao,
                ano=2026,
                mes=7,
                data_inicial=date(2026, 7, 1),
                data_final=date(2026, 7, 31),
            )
        )

        self.fixture = (
            Path(__file__).parent
            / "tests"
            / "fixtures"
            / "ofx"
            / "extrato_referencia_julho_2026.ofx"
        )

        self.url = reverse(
            "admin:financeiro_importacaoofx_changelist"
        )

        self.client.force_login(
            self.usuario
        )

    def importar(self):
        importacao, criada = importar_ofx(
            self.fixture,
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=self.competencia,
            usuario=self.usuario,
        )

        self.assertTrue(criada)

        return importacao

    def test_desfaz_importacao_apos_confirmacao(
        self,
    ):
        importacao = self.importar()

        quantidade_ofx = (
            importacao.movimentos.count()
        )

        self.assertGreater(
            quantidade_ofx,
            0,
        )

        movimento_manual = (
            MovimentacaoFinanceira.objects.create(
                empresa=self.empresa,
                termo=self.termo,
                prestacao=self.prestacao,
                competencia=self.competencia,
                data=date(2026, 7, 15),
                tipo=(
                    MovimentacaoFinanceira.Tipo
                    .REPASSE
                ),
                valor=Decimal("100.00"),
                descricao="Movimento manual preservado",
                criado_por=self.usuario,
            )
        )

        resposta_confirmacao = self.client.post(
            self.url,
            {
                "action": "desfazer_importacao_ofx",
                "_selected_action": [
                    str(importacao.pk)
                ],
                "index": "0",
            },
        )

        self.assertEqual(
            resposta_confirmacao.status_code,
            200,
        )

        self.assertContains(
            resposta_confirmacao,
            "Confirmar desfazer importacao OFX",
        )

        self.assertContains(
            resposta_confirmacao,
            str(quantidade_ofx),
        )

        self.assertTrue(
            ImportacaoOFX.objects.filter(
                pk=importacao.pk
            ).exists()
        )

        self.assertEqual(
            importacao.movimentos.count(),
            quantidade_ofx,
        )

        resposta_final = self.client.post(
            self.url,
            {
                "action": "desfazer_importacao_ofx",
                "_selected_action": [
                    str(importacao.pk)
                ],
                "confirmar": "sim",
            },
            follow=True,
        )

        self.assertEqual(
            resposta_final.status_code,
            200,
        )

        self.assertFalse(
            ImportacaoOFX.objects.filter(
                pk=importacao.pk
            ).exists()
        )

        self.assertFalse(
            MovimentacaoFinanceira.objects.filter(
                importacao_ofx_id=importacao.pk
            ).exists()
        )

        self.assertTrue(
            MovimentacaoFinanceira.objects.filter(
                pk=movimento_manual.pk
            ).exists()
        )

    def test_nao_desfaz_duas_importacoes_de_uma_vez(
        self,
    ):
        importacao_a = ImportacaoOFX.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            nome_arquivo="a.ofx",
            hash_arquivo="a" * 64,
            banco="001",
            conta_mascarada="***1234",
            tipo_conta="CHECKING",
            moeda="BRL",
            data_inicio=date(2026, 7, 1),
            data_fim=date(2026, 7, 31),
            quantidade_movimentos=0,
            importado_por=self.usuario,
        )

        importacao_b = ImportacaoOFX.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            nome_arquivo="b.ofx",
            hash_arquivo="b" * 64,
            banco="001",
            conta_mascarada="***1234",
            tipo_conta="CHECKING",
            moeda="BRL",
            data_inicio=date(2026, 7, 1),
            data_fim=date(2026, 7, 31),
            quantidade_movimentos=0,
            importado_por=self.usuario,
        )

        resposta = self.client.post(
            self.url,
            {
                "action": "desfazer_importacao_ofx",
                "_selected_action": [
                    str(importacao_a.pk),
                    str(importacao_b.pk),
                ],
                "index": "0",
            },
            follow=True,
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertTrue(
            ImportacaoOFX.objects.filter(
                pk=importacao_a.pk
            ).exists()
        )

        self.assertTrue(
            ImportacaoOFX.objects.filter(
                pk=importacao_b.pk
            ).exists()
        )

    def test_nao_desfaz_importacao_com_conciliacao_manual(
        self,
    ):
        importacao = self.importar()

        movimento = (
            importacao.movimentos
            .filter(
                tipo=(
                    MovimentacaoFinanceira.Tipo
                    .DEBITO_AUTORIZADO
                )
            )
            .first()
        )

        self.assertIsNotNone(
            movimento
        )

        lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=self.competencia,
            numero_lancamento="OFX-CONC-001",
            data_documento=date(2026, 7, 15),
            data_pagamento=date(2026, 7, 15),
            descricao="Despesa conciliada teste",
            valor_documento=movimento.valor,
            criado_por=self.usuario,
        )

        conciliacao = (
            ConciliacaoFinanceira.objects.create(
                movimentacao=movimento,
                lancamento=lancamento,
                status=(
                    ConciliacaoFinanceira.Status
                    .CONFIRMADO
                ),
                decidido_por=self.usuario,
            )
        )

        resposta = self.client.post(
            self.url,
            {
                "action": "desfazer_importacao_ofx",
                "_selected_action": [
                    str(importacao.pk)
                ],
                "index": "0",
            },
            follow=True,
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertTrue(
            ImportacaoOFX.objects.filter(
                pk=importacao.pk
            ).exists()
        )

        self.assertTrue(
            MovimentacaoFinanceira.objects.filter(
                pk=movimento.pk
            ).exists()
        )

        self.assertTrue(
            ConciliacaoFinanceira.objects.filter(
                pk=conciliacao.pk
            ).exists()
        )
