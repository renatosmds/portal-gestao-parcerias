from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    FolhaPonto,
    Funcionario,
)


class InterfaceTrabalhistaTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_superuser(
            username="interface_trabalhista",
            email="interface@pgp.local",
            password="SenhaTeste123!",
        )

        self.client.force_login(
            self.user
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Interface Trabalhista",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Interface",
            usuario="colaborador-interface",
            cpf="52998224725",
            empresa=self.empresa,
            ativo=True,
            data_admissao=date(
                2026,
                10,
                1,
            ),
            salarioBase=Decimal(
                "2200.00"
            ),
            divisor_mensal=220,
        )

    def test_criacao_gera_calendario_diario(self):

        response = self.client.post(
            reverse(
                "folha_ponto_create"
            ),
            {
                "funcionario": (
                    self.funcionario.pk
                ),
                "competencia": (
                    "2026-10-01"
                ),
                "observacoes": "",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        folha = FolhaPonto.objects.get(
            funcionario=self.funcionario,
            competencia=date(
                2026,
                10,
                1,
            ),
        )

        self.assertEqual(
            folha.dias.count(),
            31,
        )

    def test_tela_ponto_exibe_calendario_e_processamento(
        self
    ):

        folha = FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(
                2026,
                10,
                1,
            ),
        )

        response = self.client.get(
            reverse(
                "folha_ponto_update",
                args=[
                    folha.pk
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Calendário diário",
        )

        self.assertContains(
            response,
            "Processar competência",
        )

        self.assertContains(
            response,
            "Entrada 1",
        )

    def test_lista_contracheques_nao_oferece_cadastro_manual(
        self
    ):

        response = self.client.get(
            reverse(
                "folhas_pagamento_list"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotContains(
            response,
            "Novo contracheque",
        )

        self.assertContains(
            response,
            "Ir para Folhas de Ponto",
        )

    def test_banco_horas_integrado_abre(
        self
    ):

        response = self.client.get(
            reverse(
                "banco_horas_integrado"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Banco de Horas",
        )

        self.assertContains(
            response,
            "saldo atual",
        )

    def test_listagem_ponto_exibe_separacao_folha_banco(
        self
    ):

        FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(
                2026,
                10,
                1,
            ),
        )

        response = self.client.get(
            reverse(
                "folhas_ponto_list"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "HE folha",
        )

        self.assertContains(
            response,
            "HE banco",
        )
