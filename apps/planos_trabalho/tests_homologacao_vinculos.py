import os
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.lancamentos.models import Lancamento

from .models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
    VinculoLancamentoItemPlano,
)


class VinculosPlanoInterfaceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command(
            "preparar_demo_ciclo_completo",
            verbosity=0,
        )

        User = get_user_model()

        cls.usuario = User.objects.get(
            username=os.getenv("DEMO_ADMIN_USERNAME", "demo_admin")
        )

        cls.lancamento = (
            Lancamento.objects
            .filter(
                termo__numtermo="001/2026",
            )
            .order_by("pk")
            .first()
        )

        cls.termo = cls.lancamento.termo

        cls.plano = PlanoTrabalho.objects.create(
            termo=cls.termo,
            versao=1,
            titulo="Plano teste de vínculos",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            data_eficacia=date(2026, 1, 1),
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_aprovacao=date(2026, 1, 1),
        )

        cls.item = ItemPlanoTrabalho.objects.create(
            plano=cls.plano,
            codigo="ITEM-TESTE",
            rubrica_nivel_1="Custeio",
            descricao="Item teste",
            unidade="unidade",
            quantidade_prevista=Decimal("1.0000"),
            valor_unitario_previsto=Decimal("100.00"),
            valor_total_previsto=Decimal("100.00"),
            inicio_execucao=date(2026, 1, 1),
            fim_execucao=date(2026, 12, 31),
            ativo=True,
        )

    def setUp(self):
        self.client.force_login(
            self.usuario
        )

    def test_tela_lista_apenas_lancamentos_do_termo(self):
        response = self.client.get(
            reverse(
                "planos_trabalho:item_vinculos",
                args=[self.item.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            self.lancamento.numero_lancamento,
        )

        self.assertNotContains(
            response,
            "02-RH-01",
        )

    def test_post_cria_vinculo_ativo(self):
        response = self.client.post(
            reverse(
                "planos_trabalho:item_vinculos",
                args=[self.item.pk],
            ),
            {
                "lancamentos": [
                    str(self.lancamento.pk)
                ],
                "justificativa": (
                    "Vínculo manual de teste."
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        vinculo = (
            VinculoLancamentoItemPlano.objects
            .get(
                lancamento=self.lancamento,
                ativo=True,
            )
        )

        self.assertEqual(
            vinculo.item_plano,
            self.item,
        )

        self.assertEqual(
            vinculo.quantidade_executada,
            Decimal("1.0000"),
        )

        self.assertEqual(
            vinculo.valor_unitario_executado,
            self.lancamento.valor_documento,
        )

    def test_post_sem_selecao_desativa_vinculo_do_item(self):
        VinculoLancamentoItemPlano.objects.create(
            lancamento=self.lancamento,
            item_plano=self.item,
            origem=(
                VinculoLancamentoItemPlano
                .OrigemVinculo
                .MANUAL
            ),
            quantidade_executada=Decimal("1.0000"),
            valor_unitario_executado=(
                self.lancamento.valor_documento
            ),
            unidade_executada="unidade",
            ativo=True,
        )

        response = self.client.post(
            reverse(
                "planos_trabalho:item_vinculos",
                args=[self.item.pk],
            ),
            {},
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            VinculoLancamentoItemPlano.objects
            .filter(
                lancamento=self.lancamento,
                item_plano=self.item,
                ativo=True,
            )
            .exists()
        )
