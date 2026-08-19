from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.diligencias.models import (
    Diligencia,
    RespostaDiligencia,
)
from apps.empresas.models import Empresa
from apps.pareceres.diligencias import (
    criar_diligencia_do_item,
)
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)
from apps.pareceres.saneamento import (
    concluir_reanalise_diligencia,
    iniciar_reanalise_diligencia,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint467SaneamentoDiligenciaTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="analista467",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.7",
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
            codigo="SAN-001",
            titulo="Pendencia sujeita a saneamento",
            fato_verificado="Documento necessita complemento.",
            evidencia="Documento apresentado pela OSC.",
            fundamentacao="Fundamentacao registrada.",
            recomendacao="Solicitar documento complementar.",
            criado_por=self.usuario,
        )

        self.diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        self.item.refresh_from_db()

    def registrar_resposta(self):
        return RespostaDiligencia.objects.create(
            diligencia=self.diligencia,
            texto="Documento complementar apresentado.",
            criada_por=self.usuario,
        )

    def test_nao_inicia_reanalise_sem_resposta(self):
        with self.assertRaises(ValidationError):
            iniciar_reanalise_diligencia(
                item=self.item,
                usuario=self.usuario,
            )

    def test_resposta_nao_sana_automaticamente(self):
        self.registrar_resposta()

        self.item.refresh_from_db()

        self.assertEqual(
            self.item.conclusao_item,
            ItemParecer.ConclusaoItem.NAO_ANALISADO,
        )

    def test_inicia_reanalise_sem_concluir_item(self):
        self.registrar_resposta()

        diligencia = iniciar_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
        )

        self.item.refresh_from_db()

        self.assertEqual(
            diligencia.status,
            Diligencia.Status.REANALISE,
        )

        self.assertEqual(
            self.item.conclusao_item,
            ItemParecer.ConclusaoItem.NAO_ANALISADO,
        )

    def test_analista_pode_concluir_como_sanado(self):
        self.registrar_resposta()

        iniciar_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
        )

        item = concluir_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
            decisao="SANADO",
            manifestacao=(
                "A documentacao complementar saneou "
                "a pendencia identificada."
            ),
        )

        self.diligencia.refresh_from_db()

        self.assertEqual(
            item.conclusao_item,
            ItemParecer.ConclusaoItem.SANADO,
        )

        self.assertEqual(
            self.diligencia.status,
            Diligencia.Status.ATENDIDA,
        )

        self.assertIsNotNone(
            self.diligencia.encerrada_em
        )

    def test_analista_pode_concluir_como_nao_sanado(self):
        self.registrar_resposta()

        iniciar_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
        )

        item = concluir_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
            decisao="NAO_SANADO",
            manifestacao=(
                "Os documentos apresentados nao foram "
                "suficientes para sanar a pendencia."
            ),
        )

        self.diligencia.refresh_from_db()

        self.assertEqual(
            item.conclusao_item,
            ItemParecer.ConclusaoItem.NAO_SANADO,
        )

        self.assertEqual(
            self.diligencia.status,
            Diligencia.Status.NAO_ATENDIDA,
        )

    def test_conclusao_exige_manifestacao_humana(self):
        self.registrar_resposta()

        iniciar_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
        )

        with self.assertRaises(ValidationError):
            concluir_reanalise_diligencia(
                item=self.item,
                usuario=self.usuario,
                decisao="SANADO",
                manifestacao="",
            )

    def test_saneamento_nao_altera_conclusao_global_parecer(self):
        self.registrar_resposta()

        iniciar_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
        )

        conclusao_antes = self.parecer.tipo_conclusao

        concluir_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
            decisao="NAO_SANADO",
            manifestacao="Pendencia nao sanada.",
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.tipo_conclusao,
            conclusao_antes,
        )

        self.assertEqual(
            self.parecer.tipo_conclusao,
            ParecerTecnico.TipoConclusao.EM_ANALISE,
        )
