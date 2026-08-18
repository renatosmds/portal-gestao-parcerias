from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.metas.models import MetaExecucao
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


class PlanoTrabalhoSprint4511Tests(TestCase):

    def criar_funcionario(
        self,
        *,
        user,
        empresa,
        termo,
    ):
        return Funcionario.objects.create(
            nome=f"Funcionário {user.username}",
            usuario=user.username,
            endereco="Endereço fictício",
            bairro="Bairro fictício",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email=f"{user.username}@example.test",
            Telefone="000000000",
            user=user,
            empresa=empresa,
            termo=termo,
            imagem="funcionarios/teste.jpg",
        )

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
        self.empresa_a = Empresa.objects.create(
            nome="OSC A Sprint 45.11"
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC B Sprint 45.11"
        )

        self.termo_a = Termos.objects.create(
            empresa=self.empresa_a,
            numtermo="4511-A/26",
            termo="Termo A",
            objeto="Atendimento social às famílias",
        )

        self.termo_b = Termos.objects.create(
            empresa=self.empresa_b,
            numtermo="4511-B/26",
            termo="Termo B",
            objeto="Projeto ambiental",
        )

        self.user_a = User.objects.create_user(
            username="osc_a_4511",
            password="teste123",
        )

        self.user_b = User.objects.create_user(
            username="osc_b_4511",
            password="teste123",
        )

        self.criar_funcionario(
            user=self.user_a,
            empresa=self.empresa_a,
            termo=self.termo_a,
        )

        self.criar_funcionario(
            user=self.user_b,
            empresa=self.empresa_b,
            termo=self.termo_b,
        )

        self.plano_a = PlanoTrabalho.objects.create(
            termo=self.termo_a,
            versao=1,
            titulo="Plano OSC A",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.plano_b = PlanoTrabalho.objects.create(
            termo=self.termo_b,
            versao=1,
            titulo="Plano OSC B",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.prestacao_a = self.criar_prestacao(
            empresa=self.empresa_a,
            numtermo="4511-A/26",
        )

        self.prestacao_b = self.criar_prestacao(
            empresa=self.empresa_b,
            numtermo="4511-B/26",
        )

        self.meta_a = MetaExecucao.objects.create(
            prestacao=self.prestacao_a,
            codigo="META-A",
            titulo="Atendimento às famílias",
            descricao="Atendimento social",
            unidade="numero",
            valor_previsto=Decimal("10.00"),
        )

        self.meta_b = MetaExecucao.objects.create(
            prestacao=self.prestacao_b,
            codigo="META-B",
            titulo="Proteção ambiental",
            descricao="Ação ambiental",
            unidade="numero",
            valor_previsto=Decimal("10.00"),
        )

        self.item_a = ItemPlanoTrabalho.objects.create(
            plano=self.plano_a,
            codigo="ITEM-A",
            descricao="Material para atendimento social",
            valor_total_previsto=Decimal("1000.00"),
            inicio_execucao=date(2026, 1, 1),
            fim_execucao=date(2026, 12, 31),
            meta=self.meta_a,
        )

        self.item_b = ItemPlanoTrabalho.objects.create(
            plano=self.plano_b,
            codigo="ITEM-B",
            descricao="Material ambiental",
            valor_total_previsto=Decimal("2000.00"),
            inicio_execucao=date(2026, 1, 1),
            fim_execucao=date(2026, 12, 31),
            meta=self.meta_b,
        )

        self.client.login(
            username="osc_a_4511",
            password="teste123",
        )

    def test_lista_exibe_apenas_planos_da_propria_osc(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:plano_lista"
            )
        )

        self.assertContains(
            response,
            "Plano OSC A",
        )

        self.assertNotContains(
            response,
            "Plano OSC B",
        )

    def test_nao_acessa_detalhe_de_outra_osc(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:plano_detalhe",
                kwargs={"pk": self.plano_b.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_nao_edita_plano_de_outra_osc(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:plano_editar",
                kwargs={"pk": self.plano_b.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_nao_cria_item_em_plano_de_outra_osc(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:item_criar",
                kwargs={
                    "plano_pk": self.plano_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_nao_edita_item_de_outra_osc(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:item_editar",
                kwargs={
                    "pk": self.item_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_form_plano_limita_termos_por_empresa(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:plano_criar"
            )
        )

        queryset = (
            response.context[
                "form"
            ].fields[
                "termo"
            ].queryset
        )

        self.assertIn(
            self.termo_a,
            queryset,
        )

        self.assertNotIn(
            self.termo_b,
            queryset,
        )

    def test_form_item_limita_metas_por_termo_e_empresa(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:item_criar",
                kwargs={
                    "plano_pk": self.plano_a.pk,
                },
            )
        )

        queryset = (
            response.context[
                "form"
            ].fields[
                "meta"
            ].queryset
        )

        self.assertIn(
            self.meta_a,
            queryset,
        )

        self.assertNotIn(
            self.meta_b,
            queryset,
        )

    def test_analise_plano_responde_200(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:plano_analise",
                kwargs={
                    "pk": self.plano_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Conclusão executiva",
        )

    def test_analise_item_responde_200(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:item_analise",
                kwargs={
                    "pk": self.item_a.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Financeiro",
        )

        self.assertContains(
            response,
            "Meta / Objeto",
        )

    def test_nao_analisa_plano_de_outra_osc(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:plano_analise",
                kwargs={
                    "pk": self.plano_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )
