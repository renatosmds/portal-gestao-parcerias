from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)
from apps.termos.models import Termos


class PlanoTrabalhoInterfaceSprint4521Tests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="pt4521",
            password="teste123",
        )

        permissao_plano = Permission.objects.get(
            content_type__app_label="planos_trabalho",
            codename="view_planotrabalho",
        )

        self.user.user_permissions.add(
            permissao_plano
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.2.1"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT4521/26",
            termo="Termo Sprint 45.2.1",
        )

        self.plano = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano Interface",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
        )

        Funcionario.objects.create(
            nome="Usuário Sprint 45.2.1",
            usuario="pt4521",
            endereco="Endereço fictício",
            bairro="Bairro fictício",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="pt4521@example.test",
            Telefone="000000000",
            user=self.user,
            empresa=self.empresa,
            termo=self.termo,
            imagem="funcionarios/teste.jpg",
        )

        self.client.login(
            username="pt4521",
            password="teste123",
        )

    def test_lista_planos_responde_200(self):

        response = self.client.get(
            reverse(
                "planos_trabalho:plano_lista"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_detalhe_plano_responde_200(self):

        response = self.client.get(
            reverse(
                "planos_trabalho:plano_detalhe",
                kwargs={
                    "pk": self.plano.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_pode_cadastrar_item(self):

        response = self.client.post(
            reverse(
                "planos_trabalho:item_criar",
                kwargs={
                    "plano_pk": self.plano.pk,
                },
            ),
            {
                "codigo": "RH-001",
                "rubrica_nivel_1": "Pessoal",
                "rubrica_nivel_2": "Remuneração",
                "rubrica_nivel_3": "Salário",
                "descricao": "Administrador",
                "unidade": "mês",
                "quantidade_prevista": "12",
                "valor_unitario_previsto": "3000.00",
                "valor_total_previsto": "36000.00",
                "ativo": "on",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            ItemPlanoTrabalho.objects.filter(
                plano=self.plano,
                codigo="RH-001",
            ).exists()
        )

    def test_usuario_nao_autenticado_e_redirecionado(self):

        self.client.logout()

        response = self.client.get(
            reverse(
                "planos_trabalho:plano_lista"
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_lista_exibe_plano_existente(self):

        response = self.client.get(
            reverse(
                "planos_trabalho:plano_lista"
            )
        )

        self.assertContains(
            response,
            "Plano Interface",
        )

