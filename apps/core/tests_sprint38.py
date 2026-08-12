import tempfile

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.diligencias.models import Diligencia
from apps.metas.models import MetaExecucao
from apps.prestacao.models import Prestacao


MEDIA_TEMP = tempfile.mkdtemp(prefix="pgp_sprint38_")


@override_settings(MEDIA_ROOT=MEDIA_TEMP)
class CenariosDemoSprint38Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("preparar_demo_ciclo_completo", verbosity=0)

    def test_tres_cenarios_foram_criados(self):
        for numero in ("001/2026", "002/2026", "003/2026"):
            with self.subTest(termo=numero):
                self.assertTrue(
                    Prestacao.objects.filter(numtermo=numero).exists()
                )

    def test_cenario_regular(self):
        prestacao = Prestacao.objects.get(numtermo="001/2026")

        self.assertEqual(
            prestacao.situacao_workflow,
            Prestacao.SituacaoWorkflow.APROVADA,
        )

        metas = MetaExecucao.objects.filter(prestacao=prestacao)

        self.assertEqual(metas.count(), 3)
        self.assertEqual(
            metas.filter(
                situacao=MetaExecucao.Situacao.ATINGIDA
            ).count(),
            3,
        )

    def test_cenario_em_acompanhamento(self):
        prestacao = Prestacao.objects.get(numtermo="002/2026")

        self.assertEqual(
            prestacao.situacao_workflow,
            Prestacao.SituacaoWorkflow.DILIGENCIA,
        )

        diligencia = Diligencia.objects.get(prestacao=prestacao)

        self.assertEqual(
            diligencia.prioridade,
            Diligencia.Prioridade.ALTA,
        )
        self.assertEqual(
            diligencia.status,
            Diligencia.Status.VISUALIZADA,
        )

        self.assertGreaterEqual(
            diligencia.prazo_resposta,
            timezone.localdate(),
        )

    def test_cenario_critico(self):
        prestacao = Prestacao.objects.get(numtermo="003/2026")

        self.assertEqual(
            prestacao.situacao_workflow,
            Prestacao.SituacaoWorkflow.DILIGENCIA,
        )

        diligencia = Diligencia.objects.get(prestacao=prestacao)

        self.assertEqual(
            diligencia.prioridade,
            Diligencia.Prioridade.URGENTE,
        )
        self.assertEqual(
            diligencia.status,
            Diligencia.Status.EM_RESPOSTA,
        )
        self.assertLess(
            diligencia.prazo_resposta,
            timezone.localdate(),
        )

        metas_atrasadas = MetaExecucao.objects.filter(
            prestacao=prestacao,
            fim__lt=timezone.localdate(),
            situacao=MetaExecucao.Situacao.NAO_ATINGIDA,
        )

        self.assertEqual(metas_atrasadas.count(), 3)
