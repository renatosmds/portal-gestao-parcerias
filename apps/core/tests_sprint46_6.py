from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.diligencias.models import Diligencia
from apps.empresas.models import Empresa
from apps.pareceres.diligencias import criar_diligencia_do_item
from apps.pareceres.models import ItemParecer, ParecerTecnico
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint466IntegracaoDiligenciaTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="analista466",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.6",
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
            codigo="DIL-001",
            titulo="Documento necessita esclarecimento",
            fato_verificado=(
                "Foi identificada divergencia no documento."
            ),
            evidencia=(
                "Documento apresentado pela OSC."
            ),
            fundamentacao=(
                "Fundamentacao registrada no item."
            ),
            recomendacao=(
                "Solicitar esclarecimentos e documento complementar."
            ),
            criado_por=self.usuario,
        )

    def test_cria_diligencia_em_rascunho(self):
        diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        self.assertEqual(
            diligencia.status,
            Diligencia.Status.RASCUNHO,
        )

        self.assertEqual(
            diligencia.prioridade,
            Diligencia.Prioridade.NORMAL,
        )

        self.assertEqual(
            diligencia.empresa,
            self.empresa,
        )

        self.assertEqual(
            diligencia.prestacao,
            self.prestacao,
        )

    def test_vincula_diligencia_ao_item(self):
        diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        self.item.refresh_from_db()

        self.assertEqual(
            self.item.diligencia,
            diligencia,
        )

    def test_preserva_fato_e_fundamento(self):
        diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        self.assertIn(
            "Foi identificada divergencia no documento.",
            diligencia.descricao,
        )

        self.assertEqual(
            diligencia.fundamento,
            "Fundamentacao registrada no item.",
        )

    def test_prazo_e_prioridade_sao_definidos_explicitamente(self):
        prazo = date(2026, 9, 15)

        diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
            prazo_resposta=prazo,
            prioridade=Diligencia.Prioridade.ALTA,
        )

        self.assertEqual(
            diligencia.prazo_resposta,
            prazo,
        )

        self.assertEqual(
            diligencia.prioridade,
            Diligencia.Prioridade.ALTA,
        )

    def test_nao_altera_conclusao_do_item_ou_parecer(self):
        conclusao_item = self.item.conclusao_item
        conclusao_parecer = self.parecer.tipo_conclusao

        criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
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

        self.assertEqual(
            self.item.conclusao_item,
            ItemParecer.ConclusaoItem.NAO_ANALISADO,
        )

    def test_nao_cria_segunda_diligencia_para_mesmo_item(self):
        criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        self.item.refresh_from_db()

        with self.assertRaises(ValidationError):
            criar_diligencia_do_item(
                item=self.item,
                usuario=self.usuario,
            )
