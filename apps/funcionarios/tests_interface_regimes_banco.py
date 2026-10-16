from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    Funcionario,
    RegimeBancoHoras,
)


class InterfaceRegimesBancoHorasTests(
    TestCase
):

    def setUp(self):

        self.user = (
            User.objects.create_superuser(
                username="teste-regime-banco",
                email="teste-regime@example.com",
                password="senha123",
            )
        )

        self.client.force_login(
            self.user
        )

        self.empresa = (
            Empresa.objects.create(
                nome="OSC Regime Banco",
            )
        )

        self.funcionario = (
            Funcionario.objects.create(
                nome="Colaborador Banco",
                usuario="colaborador-banco",
                cpf="52998224725",
                empresa=self.empresa,
                ativo=True,
                data_admissao=date(
                    2026,
                    1,
                    1,
                ),
                salarioBase=Decimal(
                    "2200.00"
                ),
            )
        )

    def test_lista_regimes_abre(self):

        response = self.client.get(
            reverse(
                "regimes_banco_horas_list"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Regimes de Banco de Horas",
        )

    def test_banco_exibe_link_regimes(self):

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
            "Regimes de Banco de Horas",
        )

    def test_cria_regime_pela_interface(self):

        response = self.client.post(
            reverse(
                "regime_banco_horas_create"
            ),
            {
                "funcionario": (
                    self.funcionario.pk
                ),
                "tipo": "individual_6m",
                "data_inicio": "2026-11-01",
                "data_fim": "",
                "prazo_compensacao_meses": "6",
                "tratamento_vencimento": (
                    "pagar"
                ),
                "fundamento": (
                    "Acordo individual escrito "
                    "para teste funcional."
                ),
                "referencia_documento": (
                    "Acordo individual 01/11/2026"
                ),
                "ativo": "on",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        regime = (
            RegimeBancoHoras.objects.get(
                funcionario=self.funcionario
            )
        )

        self.assertEqual(
            regime.tipo,
            "individual_6m",
        )

        self.assertEqual(
            regime.prazo_compensacao_meses,
            6,
        )

        self.assertTrue(
            regime.ativo
        )

    def test_edita_regime_pela_interface(self):

        regime = (
            RegimeBancoHoras.objects.create(
                funcionario=self.funcionario,
                tipo="individual_6m",
                data_inicio=date(
                    2026,
                    11,
                    1,
                ),
                prazo_compensacao_meses=6,
                tratamento_vencimento="pagar",
                ativo=True,
            )
        )

        response = self.client.post(
            reverse(
                "regime_banco_horas_update",
                kwargs={
                    "pk": regime.pk,
                },
            ),
            {
                "funcionario": (
                    self.funcionario.pk
                ),
                "tipo": "individual_6m",
                "data_inicio": "2026-11-01",
                "data_fim": "",
                "prazo_compensacao_meses": "6",
                "tratamento_vencimento": (
                    "manual"
                ),
                "fundamento": (
                    "Fundamento atualizado."
                ),
                "referencia_documento": (
                    "Documento atualizado"
                ),
                "ativo": "on",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        regime.refresh_from_db()

        self.assertEqual(
            regime.tratamento_vencimento,
            "manual",
        )

        self.assertEqual(
            regime.referencia_documento,
            "Documento atualizado",
        )

    def test_data_final_anterior_e_rejeitada(self):

        response = self.client.post(
            reverse(
                "regime_banco_horas_create"
            ),
            {
                "funcionario": (
                    self.funcionario.pk
                ),
                "tipo": "individual_6m",
                "data_inicio": "2026-11-10",
                "data_fim": "2026-11-01",
                "prazo_compensacao_meses": "6",
                "tratamento_vencimento": (
                    "pagar"
                ),
                "fundamento": "",
                "referencia_documento": "",
                "ativo": "on",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            (
                "O fim da vigencia nao pode "
                "ser anterior ao inicio."
            ),
        )

        self.assertEqual(
            RegimeBancoHoras.objects.count(),
            0,
        )

    def test_edicao_exibe_data_inicio_no_input(self):

        regime = (
            RegimeBancoHoras.objects.create(
                funcionario=self.funcionario,
                tipo="individual_6m",
                data_inicio=date(
                    2026,
                    11,
                    1,
                ),
                prazo_compensacao_meses=6,
                tratamento_vencimento="pagar",
                ativo=True,
            )
        )

        response = self.client.get(
            reverse(
                "regime_banco_horas_update",
                kwargs={
                    "pk": regime.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            'value="2026-11-01"',
            html=False,
        )
