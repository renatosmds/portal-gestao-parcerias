from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.prestacao.models import Prestacao

from .models import ParecerTecnico


class CriacaoParecerHomologacaoTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.usuario = User.objects.create_superuser(
            username="homologador_parecer",
            email="homologador_parecer@example.test",
            password="teste12345",
        )

        cls.empresa = Empresa.objects.create(
            nome="OSC Homologa??o Parecer",
        )

        cls.prestacao = Prestacao.objects.create(
            tipo="MENSAL",
            numtermo="001/2026",
            empresa=cls.empresa,
        )

    def setUp(self):
        self.client.force_login(
            self.usuario
        )

    def test_lista_exibe_botao_novo_parecer(self):
        response = self.client.get(
            reverse(
                "pareceres:parecer_lista"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Novo Parecer",
        )

    def test_tela_criacao_exibe_prestacao(self):
        response = self.client.get(
            reverse(
                "pareceres:parecer_novo"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "001/2026",
        )

    def test_cria_parecer_inicial_em_rascunho(self):
        response = self.client.post(
            reverse(
                "pareceres:parecer_novo"
            ),
            {
                "prestacao": self.prestacao.pk,
                "numero": "PT-001/2026",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        parecer = ParecerTecnico.objects.get(
            prestacao=self.prestacao
        )

        self.assertEqual(
            parecer.empresa,
            self.empresa,
        )

        self.assertEqual(
            parecer.versao,
            1,
        )

        self.assertEqual(
            parecer.situacao,
            ParecerTecnico.Situacao.RASCUNHO,
        )

        self.assertEqual(
            parecer.tipo_conclusao,
            ParecerTecnico.TipoConclusao.EM_ANALISE,
        )

        self.assertEqual(
            parecer.elaborado_por,
            self.usuario,
        )

    def test_prestacao_com_parecer_nao_fica_disponivel(self):
        ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            numero="PT-EXISTENTE",
            elaborado_por=self.usuario,
        )

        response = self.client.get(
            reverse(
                "pareceres:parecer_novo"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        ids = list(
            response.context[
                "form"
            ].fields[
                "prestacao"
            ].queryset.values_list(
                "pk",
                flat=True,
            )
        )

        self.assertNotIn(
            self.prestacao.pk,
            ids,
        )

    def test_detalhe_prestacao_exibe_atalho_parecer(self):
        response = self.client.get(
            reverse(
                "detail_prestacao",
                args=[
                    self.prestacao.pk
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Gerar Parecer T?cnico",
        )
