from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PlanoTrabalhoSprint45111Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.11.1"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="45111/26",
            termo="Termo Sprint 45.11.1",
            objeto="Atendimento social",
        )

        self.user = User.objects.create_user(
            username="usuario45111",
            password="teste123",
        )

        Funcionario.objects.create(
            nome="Usuário Sprint 45.11.1",
            usuario="usuario45111",
            endereco="Endereço fictício",
            bairro="Bairro fictício",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="usuario45111@example.test",
            Telefone="000000000",
            user=self.user,
            empresa=self.empresa,
            termo=self.termo,
            imagem="funcionarios/teste.jpg",
        )

        self.plano = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano 45.11.1",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.item = ItemPlanoTrabalho.objects.create(
            plano=self.plano,
            codigo="MAT-001",
            descricao="Material de expediente",
            quantidade_prevista=Decimal("10.0000"),
            valor_unitario_previsto=Decimal("50.00"),
            valor_total_previsto=Decimal("500.00"),
            inicio_execucao=date(2026, 1, 1),
            fim_execucao=date(2026, 12, 31),
        )

        self.client.login(
            username="usuario45111",
            password="teste123",
        )

    def test_resultado_consolidado_expoe_codigo_item(self):
        resultado = (
            motor_regras
            .analisar_item_plano_completo(
                self.item
            )
        )

        self.assertEqual(
            resultado.item_codigo,
            "MAT-001",
        )

    def test_tela_plano_exibe_codigo_item(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:plano_analise",
                kwargs={"pk": self.plano.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MAT-001")

    def test_tela_item_nao_exibe_booleanos_python(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:item_analise",
                kwargs={"pk": self.item.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

        conteudo = response.content.decode("utf-8")

        self.assertNotIn(">True<", conteudo)
        self.assertNotIn(">False<", conteudo)
