from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos


class ResumoCompetenciaViewSegurancaTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="teste_resumo_view",
            password="teste123",
        )

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal",
        )

        self.usuario.groups.add(grupo)

        permissao = Permission.objects.get(
            codename="view_movimentacaofinanceira",
        )

        self.usuario.user_permissions.add(
            permissao
        )

        self.empresa_a = Empresa.objects.create(
            nome="OSC Empresa A",
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC Empresa B",
        )

        self.termo_a = Termos.objects.create(
            empresa=self.empresa_a,
            numtermo="A-001/2026",
            termo="Termo A",
        )

        self.termo_b = Termos.objects.create(
            empresa=self.empresa_b,
            numtermo="B-001/2026",
            termo="Termo B",
        )

        self.prestacao_a = Prestacao.objects.create(
            empresa=self.empresa_a,
            termo=self.termo_a,
            tipo="MENSAL",
            numtermo="A-001/2026",
        )

        self.prestacao_b = Prestacao.objects.create(
            empresa=self.empresa_b,
            termo=self.termo_b,
            tipo="MENSAL",
            numtermo="B-001/2026",
        )

        self.competencia_a = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao_a,
                ano=2026,
                mes=1,
                data_inicial=date(2026, 1, 1),
                data_final=date(2026, 1, 31),
                saldo_inicial=Decimal("0.00"),
                saldo_final=Decimal("0.00"),
            )
        )

        self.competencia_b = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao_b,
                ano=2026,
                mes=1,
                data_inicial=date(2026, 1, 1),
                data_final=date(2026, 1, 31),
                saldo_inicial=Decimal("0.00"),
                saldo_final=Decimal("0.00"),
            )
        )

        self.client.force_login(
            self.usuario
        )

    def test_nao_exibe_resumo_de_competencia_de_outra_empresa(self):
        resposta = self.client.get(
            reverse(
                "list_movimentacoes_financeiras"
            ),
            {
                "empresa": self.empresa_a.pk,
                "termo": self.termo_a.pk,
                "prestacao": self.prestacao_a.pk,
                "competencia": self.competencia_b.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertIsNone(
            resposta.context["competencia_resumo"]
        )

        self.assertIsNone(
            resposta.context["resumo_competencia"]
        )

    def test_exibe_resumo_da_competencia_autorizada(self):
        resposta = self.client.get(
            reverse(
                "list_movimentacoes_financeiras"
            ),
            {
                "empresa": self.empresa_a.pk,
                "termo": self.termo_a.pk,
                "prestacao": self.prestacao_a.pk,
                "competencia": self.competencia_a.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertEqual(
            resposta.context[
                "competencia_resumo"
            ].pk,
            self.competencia_a.pk,
        )

        self.assertIsNotNone(
            resposta.context[
                "resumo_competencia"
            ]
        )

    def test_empresa_exibe_resumo_consolidado(self):
        resposta = self.client.get(
            reverse(
                "list_movimentacoes_financeiras"
            ),
            {
                "empresa": self.empresa_a.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertIsNotNone(
            resposta.context["resumo_consolidado"]
        )

        self.assertEqual(
            resposta.context["nivel_resumo"],
            "Empresa",
        )

        self.assertEqual(
            resposta.context["objeto_resumo"],
            self.empresa_a,
        )


    def test_termo_exibe_resumo_consolidado(self):
        resposta = self.client.get(
            reverse(
                "list_movimentacoes_financeiras"
            ),
            {
                "empresa": self.empresa_a.pk,
                "termo": self.termo_a.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertIsNotNone(
            resposta.context["resumo_consolidado"]
        )

        self.assertEqual(
            resposta.context["nivel_resumo"],
            "Termo",
        )

        self.assertEqual(
            resposta.context["objeto_resumo"],
            self.termo_a,
        )


    def test_prestacao_exibe_resumo_consolidado(self):
        resposta = self.client.get(
            reverse(
                "list_movimentacoes_financeiras"
            ),
            {
                "empresa": self.empresa_a.pk,
                "termo": self.termo_a.pk,
                "prestacao": self.prestacao_a.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertIsNotNone(
            resposta.context["resumo_consolidado"]
        )

        self.assertEqual(
            resposta.context["nivel_resumo"],
            "Prestacao",
        )

        self.assertEqual(
            resposta.context["objeto_resumo"],
            self.prestacao_a,
        )


    def test_competencia_remove_consolidado(self):
        resposta = self.client.get(
            reverse(
                "list_movimentacoes_financeiras"
            ),
            {
                "empresa": self.empresa_a.pk,
                "termo": self.termo_a.pk,
                "prestacao": self.prestacao_a.pk,
                "competencia": self.competencia_a.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertIsNone(
            resposta.context["resumo_consolidado"]
        )

        self.assertIsNotNone(
            resposta.context["resumo_competencia"]
        )

        self.assertIsNotNone(
            resposta.context["resumo_conciliacao"]
        )


    def test_prestacao_de_outro_termo_nao_e_aceita(self):
        termo_outro = Termos.objects.create(
            empresa=self.empresa_a,
            numtermo="A-002/2026",
            termo="Termo A 2",
        )

        prestacao_outro = Prestacao.objects.create(
            empresa=self.empresa_a,
            termo=termo_outro,
            tipo="MENSAL",
            numtermo="A-002/2026",
        )

        resposta = self.client.get(
            reverse(
                "list_movimentacoes_financeiras"
            ),
            {
                "empresa": self.empresa_a.pk,
                "termo": self.termo_a.pk,
                "prestacao": prestacao_outro.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertIsNone(
            resposta.context["prestacao_resumo"]
        )

        self.assertEqual(
            resposta.context["nivel_resumo"],
            "Termo",
        )

        self.assertEqual(
            resposta.context["objeto_resumo"],
            self.termo_a,
        )
