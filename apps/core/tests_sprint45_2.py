from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)
from apps.termos.models import Termos


class PlanoTrabalhoSprint452Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.2"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT452/26",
            termo="Termo Sprint 45.2",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
        )

    def criar_plano(
        self,
        versao=1,
        situacao=None,
    ):
        if situacao is None:
            situacao = (
                PlanoTrabalho.Situacao.VIGENTE
                if versao == 1
                else PlanoTrabalho.Situacao.RASCUNHO
            )

        return PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=versao,
            titulo="Plano estruturado Sprint 45.2",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=situacao,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
        )

    def test_permite_versionamento_por_termo(self):
        plano_1 = self.criar_plano(
            versao=1
        )

        plano_2 = self.criar_plano(
            versao=2
        )

        self.assertEqual(
            plano_1.termo,
            plano_2.termo,
        )

        self.assertNotEqual(
            plano_1.versao,
            plano_2.versao,
        )

    def test_nao_permite_mesma_versao_no_mesmo_termo(self):
        self.criar_plano(
            versao=1
        )

        with self.assertRaises(
            IntegrityError
        ):
            self.criar_plano(
                versao=1
            )

    def test_item_possui_quantidade_valor_unitario_e_total(self):
        plano = self.criar_plano()

        item = ItemPlanoTrabalho.objects.create(
            plano=plano,
            codigo="RH-001",
            rubrica_nivel_1="Pessoal",
            rubrica_nivel_2="Remuneração",
            rubrica_nivel_3="Salário",
            descricao="Administrador",
            unidade="mês",
            quantidade_prevista=Decimal("12.0000"),
            valor_unitario_previsto=Decimal("3000.00"),
            valor_total_previsto=Decimal("36000.00"),
        )

        self.assertEqual(
            item.valor_calculado,
            Decimal("36000.00"),
        )

    def test_rubrica_nao_fica_presa_ao_legado_conferencia3(self):
        plano = self.criar_plano()

        item = ItemPlanoTrabalho.objects.create(
            plano=plano,
            codigo="MUN-B-99",
            rubrica_nivel_1="Rubrica própria do ente",
            rubrica_nivel_2="Subcategoria local",
            rubrica_nivel_3="Detalhamento específico",
            descricao="Item configurável",
            valor_total_previsto=Decimal("1000.00"),
        )

        self.assertEqual(
            item.rubrica_nivel_1,
            "Rubrica própria do ente",
        )

    def test_plano_rejeita_vigencia_invertida(self):
        plano = PlanoTrabalho(
            termo=self.termo,
            versao=3,
            inicio_vigencia=date(2026, 12, 31),
            fim_vigencia=date(2026, 1, 1),
        )

        with self.assertRaises(
            ValidationError
        ):
            plano.full_clean()

