from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.planos_trabalho.models import PlanoTrabalho
from apps.planos_trabalho.services import (
    ativar_versao,
    plano_aplicavel_em,
    validar_cadeia_versoes,
)
from apps.termos.models import Termos


class PlanoTrabalhoSprint453Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.3"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT453/26",
            termo="Termo Sprint 45.3",
        )

        self.plano_1 = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano inicial",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

    def criar_versao_2(
        self,
        situacao=PlanoTrabalho.Situacao.RASCUNHO,
    ):
        return PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=2,
            titulo="Plano após remanejamento",
            versao_anterior=self.plano_1,
            origem=PlanoTrabalho.Origem.REMANEJAMENTO,
            situacao=situacao,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 7, 1),
            instrumento_alteracao="Autorização 01/2026",
            justificativa_alteracao=(
                "Remanejamento autorizado."
            ),
        )

    def test_alteracao_exige_versao_anterior(self):
        plano = PlanoTrabalho(
            termo=self.termo,
            versao=2,
            origem=PlanoTrabalho.Origem.ADITIVO,
            situacao=PlanoTrabalho.Situacao.RASCUNHO,
        )

        with self.assertRaises(
            ValidationError
        ):
            plano.full_clean()

    def test_versao_anterior_deve_ser_do_mesmo_termo(self):
        outro_termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="OUTRO/26",
            termo="Outro Termo",
        )

        outro_plano = PlanoTrabalho.objects.create(
            termo=outro_termo,
            versao=1,
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.RASCUNHO,
        )

        plano = PlanoTrabalho(
            termo=self.termo,
            versao=2,
            versao_anterior=outro_plano,
            origem=PlanoTrabalho.Origem.ADITIVO,
            situacao=PlanoTrabalho.Situacao.RASCUNHO,
        )

        with self.assertRaises(
            ValidationError
        ):
            plano.full_clean()

    def test_resolve_versao_historica_pela_data(self):
        plano_2 = self.criar_versao_2()

        ativar_versao(
            plano_2
        )

        self.plano_1.refresh_from_db()
        plano_2.refresh_from_db()

        anterior = plano_aplicavel_em(
            self.termo,
            date(2026, 6, 30),
        )

        posterior = plano_aplicavel_em(
            self.termo,
            date(2026, 7, 1),
        )

        self.assertEqual(
            anterior.pk,
            self.plano_1.pk,
        )

        self.assertEqual(
            posterior.pk,
            plano_2.pk,
        )

    def test_ativar_nova_versao_substitui_a_anterior(self):
        plano_2 = self.criar_versao_2()

        ativar_versao(
            plano_2
        )

        self.plano_1.refresh_from_db()
        plano_2.refresh_from_db()

        self.assertEqual(
            self.plano_1.situacao,
            PlanoTrabalho.Situacao.SUBSTITUIDO,
        )

        self.assertEqual(
            plano_2.situacao,
            PlanoTrabalho.Situacao.VIGENTE,
        )

    def test_nao_permite_duas_versoes_vigentes(self):
        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                self.criar_versao_2(
                    situacao=PlanoTrabalho.Situacao.VIGENTE
                )

    def test_rascunho_nao_e_considerado_plano_aplicavel(self):
        self.criar_versao_2(
            situacao=PlanoTrabalho.Situacao.RASCUNHO
        )

        resultado = plano_aplicavel_em(
            self.termo,
            date(2026, 8, 1),
        )

        self.assertEqual(
            resultado.pk,
            self.plano_1.pk,
        )

        self.assertEqual(
            validar_cadeia_versoes(
                self.termo
            ),
            [],
        )
