from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.financeiro.models import (
    ConciliacaoFinanceira,
    MovimentacaoFinanceira,
)
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos


class ConciliacaoFinanceiraManualTests(
    TestCase
):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="teste_conciliacao_manual",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Conciliacao Manual",
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="MAN-001/2026",
            termo="Termo Manual",
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="MENSAL",
            numtermo="MAN-001/2026",
        )

        self.competencia = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao,
                ano=2026,
                mes=1,
                data_inicial=date(2026, 1, 1),
                data_final=date(2026, 1, 31),
            )
        )

    def criar_movimentacao(
        self,
        valor="250.00",
    ):
        return MovimentacaoFinanceira.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=self.competencia,
            data=date(2026, 1, 10),
            tipo=(
                MovimentacaoFinanceira.Tipo
                .DEBITO_AUTORIZADO
            ),
            valor=Decimal(valor),
            descricao="Debito teste",
            criado_por=self.usuario,
        )

    def criar_lancamento(
        self,
        numero="001",
        valor="250.00",
    ):
        return Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=self.competencia,
            numero_lancamento=numero,
            data_documento=date(2026, 1, 10),
            data_pagamento=date(2026, 1, 10),
            descricao="Despesa teste",
            valor_documento=Decimal(valor),
            criado_por=self.usuario,
        )

    def test_cria_conciliacao_confirmada(self):
        movimento = self.criar_movimentacao()
        lancamento = self.criar_lancamento()

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

        self.assertEqual(
            conciliacao.status,
            ConciliacaoFinanceira.Status.CONFIRMADO,
        )

        self.assertEqual(
            conciliacao.movimentacao,
            movimento,
        )

        self.assertEqual(
            conciliacao.lancamento,
            lancamento,
        )

    def test_movimentacao_tem_apenas_uma_decisao(self):
        movimento = self.criar_movimentacao()
        lancamento_a = self.criar_lancamento(
            "001"
        )
        lancamento_b = self.criar_lancamento(
            "002"
        )

        ConciliacaoFinanceira.objects.create(
            movimentacao=movimento,
            lancamento=lancamento_a,
            status=(
                ConciliacaoFinanceira.Status
                .REJEITADO
            ),
            decidido_por=self.usuario,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ConciliacaoFinanceira.objects.create(
                    movimentacao=movimento,
                    lancamento=lancamento_b,
                    status=(
                        ConciliacaoFinanceira.Status
                        .CONFIRMADO
                    ),
                    decidido_por=self.usuario,
                )

    def test_lancamento_so_pode_ter_um_confirmado(self):
        movimento_a = self.criar_movimentacao()
        movimento_b = self.criar_movimentacao()
        lancamento = self.criar_lancamento()

        ConciliacaoFinanceira.objects.create(
            movimentacao=movimento_a,
            lancamento=lancamento,
            status=(
                ConciliacaoFinanceira.Status
                .CONFIRMADO
            ),
            decidido_por=self.usuario,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ConciliacaoFinanceira.objects.create(
                    movimentacao=movimento_b,
                    lancamento=lancamento,
                    status=(
                        ConciliacaoFinanceira.Status
                        .CONFIRMADO
                    ),
                    decidido_por=self.usuario,
                )

    def test_rejeicoes_podem_referenciar_mesmo_lancamento(self):
        movimento_a = self.criar_movimentacao()
        movimento_b = self.criar_movimentacao()
        lancamento = self.criar_lancamento()

        ConciliacaoFinanceira.objects.create(
            movimentacao=movimento_a,
            lancamento=lancamento,
            status=(
                ConciliacaoFinanceira.Status
                .REJEITADO
            ),
            decidido_por=self.usuario,
        )

        ConciliacaoFinanceira.objects.create(
            movimentacao=movimento_b,
            lancamento=lancamento,
            status=(
                ConciliacaoFinanceira.Status
                .REJEITADO
            ),
            decidido_por=self.usuario,
        )

        self.assertEqual(
            ConciliacaoFinanceira.objects.filter(
                lancamento=lancamento,
                status=(
                    ConciliacaoFinanceira.Status
                    .REJEITADO
                ),
            ).count(),
            2,
        )

    def test_impede_lancamento_de_outra_hierarquia(self):
        movimento = self.criar_movimentacao()

        outra_empresa = Empresa.objects.create(
            nome="Outra OSC",
        )

        outro_termo = Termos.objects.create(
            empresa=outra_empresa,
            numtermo="OUT-001/2026",
            termo="Outro Termo",
        )

        outra_prestacao = Prestacao.objects.create(
            empresa=outra_empresa,
            termo=outro_termo,
            tipo="MENSAL",
            numtermo="OUT-001/2026",
        )

        outra_competencia = (
            CompetenciaPrestacao.objects.create(
                prestacao=outra_prestacao,
                ano=2026,
                mes=1,
                data_inicial=date(2026, 1, 1),
                data_final=date(2026, 1, 31),
            )
        )

        outro_lancamento = Lancamento.objects.create(
            empresa=outra_empresa,
            termo=outro_termo,
            prestacao=outra_prestacao,
            competencia=outra_competencia,
            numero_lancamento="OUT-001",
            data_documento=date(2026, 1, 10),
            data_pagamento=date(2026, 1, 10),
            descricao="Outra despesa",
            valor_documento=Decimal("250.00"),
            criado_por=self.usuario,
        )

        conciliacao = ConciliacaoFinanceira(
            movimentacao=movimento,
            lancamento=outro_lancamento,
            status=(
                ConciliacaoFinanceira.Status
                .CONFIRMADO
            ),
            decidido_por=self.usuario,
        )

        with self.assertRaises(ValidationError):
            conciliacao.full_clean()

    def test_impede_tipo_nao_conciliavel(self):
        movimento = self.criar_movimentacao()

        movimento.tipo = (
            MovimentacaoFinanceira.Tipo.REPASSE
        )
        movimento.save(
            update_fields=["tipo"]
        )

        lancamento = self.criar_lancamento()

        conciliacao = ConciliacaoFinanceira(
            movimentacao=movimento,
            lancamento=lancamento,
            status=(
                ConciliacaoFinanceira.Status
                .CONFIRMADO
            ),
            decidido_por=self.usuario,
        )

        with self.assertRaises(ValidationError):
            conciliacao.full_clean()
