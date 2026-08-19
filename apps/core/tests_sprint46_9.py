from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.pareceres.models import (
    EvidenciaParecer,
    FundamentacaoParecer,
    ItemParecer,
    ParecerTecnico,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint469FundamentacaoEvidenciasTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="analista469",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.9",
        )

        self.prestacao = Prestacao.objects.create(
            tipo="MENSAL",
            empresa=self.empresa,
        )

        self.parecer = ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            elaborado_por=self.usuario,
        )

        self.item = ItemParecer.objects.create(
            parecer=self.parecer,
            codigo="FUND-001",
            titulo="Item com rastreabilidade",
            criado_por=self.usuario,
        )

    def test_cria_evidencia_estruturada(self):
        evidencia = EvidenciaParecer.objects.create(
            item=self.item,
            tipo=EvidenciaParecer.Tipo.REGISTRO_SISTEMA,
            descricao="Registro estruturado da an?lise.",
            dados_snapshot={
                "origem": "PGP Rules",
                "codigo_regra": "TESTE-001",
            },
            criado_por=self.usuario,
        )

        self.assertEqual(
            evidencia.item,
            self.item,
        )

        self.assertEqual(
            evidencia.dados_snapshot["codigo_regra"],
            "TESTE-001",
        )

    def test_permite_multiplas_evidencias_por_item(self):
        EvidenciaParecer.objects.create(
            item=self.item,
            descricao="Primeira evid?ncia.",
            criado_por=self.usuario,
        )

        EvidenciaParecer.objects.create(
            item=self.item,
            descricao="Segunda evid?ncia.",
            criado_por=self.usuario,
        )

        self.assertEqual(
            self.item.evidencias_estruturadas.count(),
            2,
        )

    def test_cria_fundamentacao_federal(self):
        fundamento = FundamentacaoParecer.objects.create(
            item=self.item,
            esfera=FundamentacaoParecer.Esfera.FEDERAL,
            ente="Uni?o",
            norma="Lei Federal n? 13.019/2014",
            dispositivo="dispositivo aplic?vel",
            descricao="Fundamento registrado no momento da an?lise.",
            origem="PGP Rules",
            dados_snapshot={
                "camada": "nacional",
            },
            criado_por=self.usuario,
        )

        self.assertEqual(
            fundamento.esfera,
            FundamentacaoParecer.Esfera.FEDERAL,
        )

        self.assertEqual(
            fundamento.dados_snapshot["camada"],
            "nacional",
        )

    def test_permite_fundamento_local_separado_do_federal(self):
        FundamentacaoParecer.objects.create(
            item=self.item,
            esfera=FundamentacaoParecer.Esfera.FEDERAL,
            norma="Lei Federal n? 13.019/2014",
            criado_por=self.usuario,
        )

        FundamentacaoParecer.objects.create(
            item=self.item,
            esfera=FundamentacaoParecer.Esfera.MUNICIPAL,
            ente="Munic?pio de teste",
            norma="Norma municipal aplic?vel",
            criado_por=self.usuario,
        )

        self.assertEqual(
            self.item.fundamentacoes_estruturadas.count(),
            2,
        )

    def test_rejeita_vigencia_invertida(self):
        fundamento = FundamentacaoParecer(
            item=self.item,
            norma="Norma de teste",
            inicio_vigencia=date(2026, 12, 31),
            fim_vigencia=date(2026, 1, 1),
            criado_por=self.usuario,
        )

        with self.assertRaises(ValidationError):
            fundamento.full_clean()

    def test_rastreabilidade_nao_altera_conclusao(self):
        conclusao_item = self.item.conclusao_item
        conclusao_parecer = self.parecer.tipo_conclusao

        EvidenciaParecer.objects.create(
            item=self.item,
            descricao="Evid?ncia.",
            criado_por=self.usuario,
        )

        FundamentacaoParecer.objects.create(
            item=self.item,
            norma="Norma aplic?vel",
            criado_por=self.usuario,
        )

        self.item.refresh_from_db()
        self.parecer.refresh_from_db()

        self.assertEqual(
            self.item.conclusao_item,
            conclusao_item,
        )

        self.assertEqual(
            self.parecer.tipo_conclusao,
            conclusao_parecer,
        )
