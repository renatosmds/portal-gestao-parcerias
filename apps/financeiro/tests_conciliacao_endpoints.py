from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

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


class ConciliacaoFinanceiraEndpointTests(
    TestCase
):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="conciliador",
            password="teste123",
        )

        permissao = Permission.objects.get(
            codename="change_movimentacaofinanceira"
        )

        self.usuario.user_permissions.add(
            permissao
        )

        grupo_global, _ = Group.objects.get_or_create(
            name="Administrador do Sistema"
        )

        self.usuario.groups.add(
            grupo_global
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Endpoint Conciliacao",
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="END-001/2026",
            termo="Termo Endpoint",
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="MENSAL",
            numtermo="END-001/2026",
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

        self.movimentacao = (
            MovimentacaoFinanceira.objects.create(
                empresa=self.empresa,
                termo=self.termo,
                prestacao=self.prestacao,
                competencia=self.competencia,
                data=date(2026, 1, 10),
                tipo=(
                    MovimentacaoFinanceira.Tipo
                    .DEBITO_AUTORIZADO
                ),
                valor=Decimal("250.00"),
                descricao="Debito endpoint",
                criado_por=self.usuario,
            )
        )

        self.lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=self.competencia,
            numero_lancamento="END-001",
            data_documento=date(2026, 1, 10),
            data_pagamento=date(2026, 1, 10),
            descricao="Despesa endpoint",
            valor_documento=Decimal("250.00"),
            criado_por=self.usuario,
        )

        self.client.force_login(
            self.usuario
        )

    def test_confirmacao_exige_post(self):
        url = reverse(
            "confirmar_conciliacao_financeira",
            args=[
                self.movimentacao.pk,
                self.lancamento.pk,
            ],
        )

        resposta = self.client.get(url)

        self.assertEqual(
            resposta.status_code,
            405,
        )

    def test_confirma_candidato(self):
        url = reverse(
            "confirmar_conciliacao_financeira",
            args=[
                self.movimentacao.pk,
                self.lancamento.pk,
            ],
        )

        resposta = self.client.post(url)

        self.assertEqual(
            resposta.status_code,
            302,
        )

        conciliacao = (
            ConciliacaoFinanceira.objects.get(
                movimentacao=self.movimentacao
            )
        )

        self.assertEqual(
            conciliacao.status,
            ConciliacaoFinanceira.Status.CONFIRMADO,
        )

        self.assertEqual(
            conciliacao.lancamento,
            self.lancamento,
        )

        self.assertEqual(
            conciliacao.decidido_por,
            self.usuario,
        )

    def test_rejeita_candidato(self):
        url = reverse(
            "rejeitar_conciliacao_financeira",
            args=[
                self.movimentacao.pk,
                self.lancamento.pk,
            ],
        )

        resposta = self.client.post(url)

        self.assertEqual(
            resposta.status_code,
            302,
        )

        conciliacao = (
            ConciliacaoFinanceira.objects.get(
                movimentacao=self.movimentacao
            )
        )

        self.assertEqual(
            conciliacao.status,
            ConciliacaoFinanceira.Status.REJEITADO,
        )

    def test_nao_permite_lancamento_que_nao_e_candidato(self):
        outro = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=self.competencia,
            numero_lancamento="END-002",
            data_documento=date(2026, 1, 20),
            data_pagamento=date(2026, 1, 20),
            descricao="Outra despesa",
            valor_documento=Decimal("999.00"),
            criado_por=self.usuario,
        )

        url = reverse(
            "confirmar_conciliacao_financeira",
            args=[
                self.movimentacao.pk,
                outro.pk,
            ],
        )

        self.client.post(url)

        self.assertFalse(
            ConciliacaoFinanceira.objects.filter(
                movimentacao=self.movimentacao
            ).exists()
        )

    def test_usuario_sem_permissao_recebe_403(self):
        User = get_user_model()

        usuario = User.objects.create_user(
            username="sem_permissao",
            password="teste123",
        )

        self.client.force_login(usuario)

        url = reverse(
            "confirmar_conciliacao_financeira",
            args=[
                self.movimentacao.pk,
                self.lancamento.pk,
            ],
        )

        resposta = self.client.post(url)

        self.assertEqual(
            resposta.status_code,
            403,
        )

    def test_confirmacao_preserva_tela_de_origem(self):
        url = reverse(
            "confirmar_conciliacao_financeira",
            args=[
                self.movimentacao.pk,
                self.lancamento.pk,
            ],
        )

        destino = (
            "/financeiro/"
            "?empresa=1&termo=2"
            "&prestacao=3&competencia=4"
        )

        resposta = self.client.post(
            url,
            {
                "next": destino,
            },
        )

        self.assertRedirects(
            resposta,
            destino,
            fetch_redirect_response=False,
        )

    def test_next_externo_nao_e_aceito(self):
        url = reverse(
            "confirmar_conciliacao_financeira",
            args=[
                self.movimentacao.pk,
                self.lancamento.pk,
            ],
        )

        resposta = self.client.post(
            url,
            {
                "next": "https://exemplo-malicioso.com/",
            },
        )

        self.assertRedirects(
            resposta,
            reverse(
                "list_movimentacoes_financeiras"
            ),
            fetch_redirect_response=False,
        )
