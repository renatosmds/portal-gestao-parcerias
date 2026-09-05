from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.prestacao.models import CompetenciaPrestacao, Prestacao
from apps.termos.models import Termos


class LancamentoDependenciasTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="usuario_dependencias",
            password="teste123",
        )

        permissoes = Permission.objects.filter(
            codename__in=[
                "add_lancamento",
                "change_lancamento",
            ]
        )
        self.usuario.user_permissions.add(*permissoes)

        self.empresa = Empresa.objects.create(
            nome="Empresa Dependencias"
        )

        Funcionario.objects.create(
            nome="Usuario Dependencias",
            usuario="usuario_dependencias",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="-",
            estado="MG",
            email="dependencias@example.com",
            Telefone="-",
            user=self.usuario,
            empresa=self.empresa,
            imagem="funcionarios_photos/teste.jpg",
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            termo="Termo de Colabora??o",
            numtermo="DEP-001/2026",
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="cnpj",
            numtermo="DEP-001/2026",
        )

        self.competencia = CompetenciaPrestacao.objects.create(
            prestacao=self.prestacao,
            ano=2026,
            mes=1,
            data_inicial="2026-01-01",
            data_final="2026-01-31",
        )

    def test_endpoint_prestacoes_exige_login(self):
        resposta = self.client.get(
            reverse("prestacoes_por_termo"),
            {"termo": self.termo.pk},
        )

        self.assertEqual(resposta.status_code, 401)

    def test_endpoint_competencias_exige_login(self):
        resposta = self.client.get(
            reverse("competencias_por_prestacao"),
            {"prestacao": self.prestacao.pk},
        )

        self.assertEqual(resposta.status_code, 401)

    def test_endpoint_prestacoes_retorna_prestacao_do_termo(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(
            reverse("prestacoes_por_termo"),
            {"termo": self.termo.pk},
        )

        self.assertEqual(resposta.status_code, 200)

        dados = resposta.json()["prestacoes"]

        self.assertEqual(len(dados), 1)
        self.assertEqual(
            dados[0]["id"],
            self.prestacao.pk,
        )

    def test_endpoint_competencias_retorna_competencia_da_prestacao(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(
            reverse("competencias_por_prestacao"),
            {"prestacao": self.prestacao.pk},
        )

        self.assertEqual(resposta.status_code, 200)

        dados = resposta.json()["competencias"]

        self.assertEqual(len(dados), 1)
        self.assertEqual(
            dados[0]["id"],
            self.competencia.pk,
        )

    def test_prestacoes_nao_misturam_termos(self):
        outro_termo = Termos.objects.create(
            empresa=self.empresa,
            termo="Termo de Colabora??o",
            numtermo="DEP-002/2026",
        )

        outra_prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=outro_termo,
            tipo="cnpj",
            numtermo="DEP-002/2026",
        )

        self.client.force_login(self.usuario)

        resposta = self.client.get(
            reverse("prestacoes_por_termo"),
            {"termo": self.termo.pk},
        )

        ids = [
            item["id"]
            for item in resposta.json()["prestacoes"]
        ]

        self.assertIn(self.prestacao.pk, ids)
        self.assertNotIn(outra_prestacao.pk, ids)

    def test_competencias_nao_misturam_prestacoes(self):
        outra_prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="cnpj",
            numtermo="DEP-003/2026",
        )

        outra_competencia = CompetenciaPrestacao.objects.create(
            prestacao=outra_prestacao,
            ano=2026,
            mes=2,
            data_inicial="2026-02-01",
            data_final="2026-02-28",
        )

        self.client.force_login(self.usuario)

        resposta = self.client.get(
            reverse("competencias_por_prestacao"),
            {"prestacao": self.prestacao.pk},
        )

        ids = [
            item["id"]
            for item in resposta.json()["competencias"]
        ]

        self.assertIn(self.competencia.pk, ids)
        self.assertNotIn(outra_competencia.pk, ids)

    def test_endpoint_prestacoes_isola_outra_empresa(self):
        outra_empresa = Empresa.objects.create(
            nome="Outra Empresa"
        )

        outro_termo = Termos.objects.create(
            empresa=outra_empresa,
            termo="Termo de Colabora??o",
            numtermo="OUT-001/2026",
        )

        outra_prestacao = Prestacao.objects.create(
            empresa=outra_empresa,
            termo=outro_termo,
            tipo="cnpj",
            numtermo="OUT-001/2026",
        )

        self.client.force_login(self.usuario)

        resposta = self.client.get(
            reverse("prestacoes_por_termo"),
            {"termo": outro_termo.pk},
        )

        self.assertEqual(resposta.status_code, 200)

        ids = [
            item["id"]
            for item in resposta.json()["prestacoes"]
        ]

        self.assertNotIn(
            outra_prestacao.pk,
            ids,
        )

    def test_endpoint_competencias_isola_outra_empresa(self):
        outra_empresa = Empresa.objects.create(
            nome="Outra Empresa Competencia"
        )

        outro_termo = Termos.objects.create(
            empresa=outra_empresa,
            termo="Termo de Colabora??o",
            numtermo="OUT-002/2026",
        )

        outra_prestacao = Prestacao.objects.create(
            empresa=outra_empresa,
            termo=outro_termo,
            tipo="cnpj",
            numtermo="OUT-002/2026",
        )

        outra_competencia = CompetenciaPrestacao.objects.create(
            prestacao=outra_prestacao,
            ano=2026,
            mes=3,
            data_inicial="2026-03-01",
            data_final="2026-03-31",
        )

        self.client.force_login(self.usuario)

        resposta = self.client.get(
            reverse("competencias_por_prestacao"),
            {"prestacao": outra_prestacao.pk},
        )

        self.assertEqual(resposta.status_code, 200)

        ids = [
            item["id"]
            for item in resposta.json()["competencias"]
        ]

        self.assertNotIn(
            outra_competencia.pk,
            ids,
        )
