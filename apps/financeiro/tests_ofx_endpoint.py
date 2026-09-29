from datetime import date
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.financeiro.models import (
    ImportacaoOFX,
    MovimentacaoFinanceira,
)
from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos


class ImportacaoOFXEndpointTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="teste_upload_ofx",
            password="teste123",
        )

        permissao = Permission.objects.get(
            codename="add_movimentacaofinanceira"
        )

        self.usuario.user_permissions.add(
            permissao
        )

        grupo_global, _ = Group.objects.get_or_create(
            name="Administrador do Sistema"
        )

        self.usuario.groups.add(
            grupo_global
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Teste OFX"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="OFX-001/2026",
            termo="Termo OFX",
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="MENSAL",
            numtermo="OFX-001/2026",
        )

        self.competencia = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao,
                ano=2026,
                mes=7,
                data_inicial=date(2026, 7, 1),
                data_final=date(2026, 7, 31),
            )
        )

        self.fixture = (
            Path(__file__).parent
            / "tests"
            / "fixtures"
            / "ofx"
            / "extrato_referencia_julho_2026.ofx"
        )

        self.url = reverse(
            "importar_ofx_financeiro"
        )

        self.client.force_login(
            self.usuario
        )

    def arquivo_ofx(self):
        return SimpleUploadedFile(
            "extrato_teste.ofx",
            self.fixture.read_bytes(),
            content_type="application/x-ofx",
        )

    def dados(self):
        return {
            "empresa": str(self.empresa.pk),
            "termo": str(self.termo.pk),
            "prestacao": str(self.prestacao.pk),
            "competencia": str(self.competencia.pk),
            "arquivo_ofx": self.arquivo_ofx(),
        }

    def test_importa_ofx_com_sucesso(self):
        resposta = self.client.post(
            self.url,
            self.dados(),
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            ImportacaoOFX.objects.count(),
            1,
        )

        self.assertTrue(
            MovimentacaoFinanceira.objects
            .filter(
                empresa=self.empresa,
                termo=self.termo,
                prestacao=self.prestacao,
                competencia=self.competencia,
            )
            .exists()
        )

    def test_exige_arquivo(self):
        dados = self.dados()
        dados.pop("arquivo_ofx")

        resposta = self.client.post(
            self.url,
            dados,
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            ImportacaoOFX.objects.count(),
            0,
        )

    def test_rejeita_extensao_invalida(self):
        dados = self.dados()

        dados["arquivo_ofx"] = (
            SimpleUploadedFile(
                "extrato.txt",
                b"arquivo invalido",
                content_type="text/plain",
            )
        )

        resposta = self.client.post(
            self.url,
            dados,
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            ImportacaoOFX.objects.count(),
            0,
        )

    def test_rejeita_competencia_de_outra_prestacao(self):
        outra_prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="MENSAL",
            numtermo="OFX-002/2026",
        )

        outra_competencia = (
            CompetenciaPrestacao.objects.create(
                prestacao=outra_prestacao,
                ano=2026,
                mes=8,
                data_inicial=date(2026, 8, 1),
                data_final=date(2026, 8, 31),
            )
        )

        dados = self.dados()

        dados["competencia"] = str(
            outra_competencia.pk
        )

        resposta = self.client.post(
            self.url,
            dados,
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            ImportacaoOFX.objects.count(),
            0,
        )

    def test_rejeita_ofx_fora_do_periodo_da_competencia(self):
        competencia_marco = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao,
                ano=2026,
                mes=3,
                data_inicial=date(2026, 3, 1),
                data_final=date(2026, 3, 31),
            )
        )

        dados = self.dados()

        dados["competencia"] = str(
            competencia_marco.pk
        )

        resposta = self.client.post(
            self.url,
            dados,
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            ImportacaoOFX.objects.count(),
            0,
        )

        self.assertEqual(
            MovimentacaoFinanceira.objects.count(),
            0,
        )


    def test_reimportacao_mesmo_arquivo_e_idempotente(self):
        resposta_1 = self.client.post(
            self.url,
            self.dados(),
        )

        self.assertEqual(
            resposta_1.status_code,
            302,
        )

        quantidade_antes = (
            MovimentacaoFinanceira.objects.count()
        )

        resposta_2 = self.client.post(
            self.url,
            self.dados(),
        )

        self.assertEqual(
            resposta_2.status_code,
            302,
        )

        self.assertEqual(
            ImportacaoOFX.objects.count(),
            1,
        )

        self.assertEqual(
            MovimentacaoFinanceira.objects.count(),
            quantidade_antes,
        )
