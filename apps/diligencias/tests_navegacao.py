from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.diligencias.models import Diligencia
from apps.documentos.models import Documento
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import Prestacao


class NavegacaoDiligenciaTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command(
            "preparar_demo_ciclo_completo",
            verbosity=0,
        )

        User = get_user_model()

        cls.usuario = User.objects.get(
            username="homologador"
        )

        cls.prestacao = Prestacao.objects.get(
            numtermo="001/2026"
        )

        cls.lancamento = (
            Lancamento.objects
            .filter(
                termo=cls.prestacao.termo,
                empresa=cls.prestacao.empresa,
            )
            .first()
        )

        cls.documento = (
            Documento.objects
            .filter(
                empresa=cls.prestacao.empresa,
                termo=cls.prestacao.termo,
                lancamento=cls.lancamento,
            )
            .first()
        )

        cls.diligencia = Diligencia.objects.create(
            assunto="Teste de navega??o",
            descricao="Homologa??o dos atalhos.",
            empresa=cls.prestacao.empresa,
            prestacao=cls.prestacao,
            lancamento=cls.lancamento,
            documento=cls.documento,
            criada_por=cls.usuario,
        )

    def setUp(self):
        self.client.force_login(
            self.usuario
        )

    def test_detalhe_exibe_navegacao_completa(self):
        response = self.client.get(
            reverse(
                "detail_diligencia",
                args=[self.diligencia.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        for texto in (
            "Voltar ?s Dilig?ncias",
            "Abrir Presta??o",
            "Abrir Lan?amento",
            "Abrir Documento",
            "Abrir Parceria",
        ):
            self.assertContains(
                response,
                texto,
            )

        self.assertIsNotNone(
            response.context["parceria"]
        )

    def test_links_apontam_para_os_registros_corretos(self):
        response = self.client.get(
            reverse(
                "detail_diligencia",
                args=[self.diligencia.pk],
            )
        )

        self.assertContains(
            response,
            reverse(
                "detail_prestacao",
                args=[self.prestacao.pk],
            ),
        )

        self.assertContains(
            response,
            reverse(
                "detail_lancamento",
                args=[self.lancamento.pk],
            ),
        )

        self.assertContains(
            response,
            reverse(
                "detail_documento",
                args=[self.documento.pk],
            ),
        )

        parceria = response.context["parceria"]

        self.assertContains(
            response,
            reverse(
                "detail_parceria",
                args=[parceria.pk],
            ),
        )
