from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.diligencias.models import Diligencia
from apps.prestacao.models import Prestacao


class DiligenciaStatusPostTests(TestCase):

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

        cls.diligencia = Diligencia.objects.create(
            assunto="Teste status POST",
            descricao="Homologa??o da movimenta??o.",
            empresa=cls.prestacao.empresa,
            prestacao=cls.prestacao,
            criada_por=cls.usuario,
            status=Diligencia.Status.RESPONDIDA,
        )

    def setUp(self):
        self.client.force_login(
            self.usuario
        )

    def test_get_status_retorna_405(self):
        response = self.client.get(
            reverse(
                "alterar_status_diligencia",
                args=[
                    self.diligencia.pk,
                    Diligencia.Status.REANALISE,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            405,
        )

    def test_post_altera_para_reanalise(self):
        response = self.client.post(
            reverse(
                "alterar_status_diligencia",
                args=[
                    self.diligencia.pk,
                    Diligencia.Status.REANALISE,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.diligencia.refresh_from_db()

        self.assertEqual(
            self.diligencia.status,
            Diligencia.Status.REANALISE,
        )

    def test_template_usa_post_para_movimentar(self):
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

        self.assertContains(
            response,
            'method="post"',
        )

        self.assertContains(
            response,
            "Em rean\u00e1lise",
        )

        self.assertContains(
            response,
            "Atendida",
        )

        self.assertContains(
            response,
            "N\u00e3o atendida",
        )

        self.assertContains(
            response,
            "Cancelar",
        )
