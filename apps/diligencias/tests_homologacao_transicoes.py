from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.diligencias.models import Diligencia
from apps.empresas.models import Empresa
from apps.prestacao.models import Prestacao


class DiligenciaTransicoesTests(TestCase):

    @classmethod
    def setUpTestData(cls):

        User = get_user_model()

        cls.usuario = User.objects.create_superuser(
            username="teste_transicoes_diligencia",
            email="transicoes@example.test",
            password="teste12345",
        )

        cls.empresa = Empresa.objects.create(
            nome="Empresa Teste Transicoes",
        )

        cls.prestacao = Prestacao.objects.create(
            empresa=cls.empresa,
            tipo="cnpj",
            numtermo="TRANS-001/2026",
        )

    def setUp(self):

        self.client.force_login(
            self.usuario
        )

    def _criar_encerrada(
        self,
        status,
    ):

        return Diligencia.objects.create(
            assunto="Teste de transicao terminal",
            descricao=(
                "Valida bloqueio de reabertura "
                "de diligencia encerrada."
            ),
            empresa=self.empresa,
            prestacao=self.prestacao,
            criada_por=self.usuario,
            status=status,
            encerrada_em=timezone.now(),
        )

    def test_atendida_nao_pode_voltar_para_reanalise(
        self,
    ):

        diligencia = self._criar_encerrada(
            Diligencia.Status.ATENDIDA
        )

        encerrada_em = diligencia.encerrada_em

        response = self.client.post(
            reverse(
                "alterar_status_diligencia",
                args=[
                    diligencia.pk,
                    Diligencia.Status.REANALISE,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        diligencia.refresh_from_db()

        self.assertEqual(
            diligencia.status,
            Diligencia.Status.ATENDIDA,
        )

        self.assertEqual(
            diligencia.encerrada_em,
            encerrada_em,
        )

    def test_nao_atendida_nao_pode_ser_reaberta(
        self,
    ):

        diligencia = self._criar_encerrada(
            Diligencia.Status.NAO_ATENDIDA
        )

        self.client.post(
            reverse(
                "alterar_status_diligencia",
                args=[
                    diligencia.pk,
                    Diligencia.Status.RESPONDIDA,
                ],
            )
        )

        diligencia.refresh_from_db()

        self.assertEqual(
            diligencia.status,
            Diligencia.Status.NAO_ATENDIDA,
        )

    def test_cancelada_nao_pode_ser_reaberta(
        self,
    ):

        diligencia = self._criar_encerrada(
            Diligencia.Status.CANCELADA
        )

        self.client.post(
            reverse(
                "alterar_status_diligencia",
                args=[
                    diligencia.pk,
                    Diligencia.Status.REANALISE,
                ],
            )
        )

        diligencia.refresh_from_db()

        self.assertEqual(
            diligencia.status,
            Diligencia.Status.CANCELADA,
        )

    def test_atendida_nao_pode_ser_enviada_novamente(
        self,
    ):

        diligencia = self._criar_encerrada(
            Diligencia.Status.ATENDIDA
        )

        encerrada_em = diligencia.encerrada_em

        response = self.client.post(
            reverse(
                "enviar_diligencia",
                args=[
                    diligencia.pk,
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        diligencia.refresh_from_db()

        self.assertEqual(
            diligencia.status,
            Diligencia.Status.ATENDIDA,
        )

        self.assertEqual(
            diligencia.encerrada_em,
            encerrada_em,
        )

    def test_cancelada_nao_aceita_nova_resposta(
        self,
    ):

        diligencia = self._criar_encerrada(
            Diligencia.Status.CANCELADA
        )

        response = self.client.post(
            reverse(
                "responder_diligencia",
                args=[
                    diligencia.pk,
                ],
            ),
            {
                "texto": (
                    "Tentativa de resposta "
                    "apos encerramento."
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        diligencia.refresh_from_db()

        self.assertEqual(
            diligencia.status,
            Diligencia.Status.CANCELADA,
        )

