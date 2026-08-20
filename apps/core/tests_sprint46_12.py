from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.diligencias.models import RespostaDiligencia
from apps.empresas.models import Empresa
from apps.pareceres.diligencias import criar_diligencia_do_item
from apps.pareceres.models import (
    HistoricoParecer,
    ItemParecer,
    ParecerTecnico,
)
from apps.pareceres.saneamento import (
    concluir_reanalise_diligencia,
    iniciar_reanalise_diligencia,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint4612AuditoriaParecerTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_superuser(
            username="auditor4612",
            email="auditor4612@example.com",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.12",
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
            codigo="AUD-001",
            titulo="Item audit?vel",
            fato_verificado="Pend?ncia identificada.",
            conclusao_item=(
                ItemParecer.ConclusaoItem.NAO_ANALISADO
            ),
            criado_por=self.usuario,
        )

    def test_revisao_parecer_gera_historico(self):
        self.client.force_login(self.usuario)

        self.client.post(
            reverse(
                "pareceres:parecer_revisar",
                args=[self.parecer.pk],
            ),
            {
                "tipo_conclusao": (
                    ParecerTecnico.TipoConclusao.COM_RESSALVAS
                ),
                "resumo_executivo": "Resumo revisado.",
                "fundamentacao_geral": "Fundamento.",
                "conclusao": "Conclus?o.",
                "ressalvas": "Ressalva.",
                "recomendacoes_gerais": "Recomenda??o.",
            },
        )

        historico = HistoricoParecer.objects.get(
            parecer=self.parecer,
            acao="REVISAO_PARECER",
        )

        self.assertEqual(
            historico.usuario,
            self.usuario,
        )

        self.assertEqual(
            historico.conclusao_anterior,
            ParecerTecnico.TipoConclusao.EM_ANALISE,
        )

        self.assertEqual(
            historico.nova_conclusao,
            ParecerTecnico.TipoConclusao.COM_RESSALVAS,
        )

    def test_revisao_item_preserva_anterior_e_novo(self):
        self.client.force_login(self.usuario)

        self.client.post(
            reverse(
                "pareceres:item_revisar",
                args=[self.item.pk],
            ),
            {
                "fato_verificado": "Fato confirmado.",
                "evidencia": "Documento conferido.",
                "fundamentacao": "Fundamento.",
                "risco_glosa": "",
                "recomendacao": "Registrar ressalva.",
                "manifestacao_analista": "Revis?o conclu?da.",
                "conclusao_item": (
                    ItemParecer.ConclusaoItem.RESSALVA
                ),
            },
        )

        historico = HistoricoParecer.objects.get(
            parecer=self.parecer,
            acao="REVISAO_ITEM",
        )

        self.assertEqual(
            historico.conclusao_anterior,
            ItemParecer.ConclusaoItem.NAO_ANALISADO,
        )

        self.assertEqual(
            historico.nova_conclusao,
            ItemParecer.ConclusaoItem.RESSALVA,
        )

        self.assertIn(
            "AUD-001",
            historico.observacao,
        )

    def test_criacao_diligencia_gera_historico(self):
        diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        historico = HistoricoParecer.objects.get(
            parecer=self.parecer,
            acao="DILIGENCIA_CRIADA",
        )

        self.assertIn(
            f"#{diligencia.pk}",
            historico.observacao,
        )

        self.assertEqual(
            historico.usuario,
            self.usuario,
        )

    def test_reanalise_gera_historico(self):
        diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        RespostaDiligencia.objects.create(
            diligencia=diligencia,
            texto="Resposta da OSC.",
            criada_por=self.usuario,
        )

        iniciar_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
        )

        self.assertTrue(
            HistoricoParecer.objects.filter(
                parecer=self.parecer,
                acao="REANALISE_INICIADA",
            ).exists()
        )

    def test_saneamento_gera_historico(self):
        diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        RespostaDiligencia.objects.create(
            diligencia=diligencia,
            texto="Documento complementar.",
            criada_por=self.usuario,
        )

        iniciar_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
        )

        concluir_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
            decisao="SANADO",
            manifestacao="Pend?ncia saneada.",
        )

        historico = HistoricoParecer.objects.get(
            parecer=self.parecer,
            acao="ITEM_SANADO",
        )

        self.assertEqual(
            historico.nova_conclusao,
            ItemParecer.ConclusaoItem.SANADO,
        )

        self.assertEqual(
            historico.usuario,
            self.usuario,
        )

    def test_nao_sanado_gera_evento_distinto(self):
        diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        RespostaDiligencia.objects.create(
            diligencia=diligencia,
            texto="Resposta insuficiente.",
            criada_por=self.usuario,
        )

        iniciar_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
        )

        concluir_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
            decisao="NAO_SANADO",
            manifestacao="Resposta insuficiente.",
        )

        self.assertTrue(
            HistoricoParecer.objects.filter(
                parecer=self.parecer,
                acao="ITEM_NAO_SANADO",
            ).exists()
        )

    def test_historico_nao_altera_conclusao_global(self):
        conclusao_antes = self.parecer.tipo_conclusao

        criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.tipo_conclusao,
            conclusao_antes,
        )

    def test_eventos_preservam_ordem_temporal(self):
        diligencia = criar_diligencia_do_item(
            item=self.item,
            usuario=self.usuario,
        )

        RespostaDiligencia.objects.create(
            diligencia=diligencia,
            texto="Resposta.",
            criada_por=self.usuario,
        )

        iniciar_reanalise_diligencia(
            item=self.item,
            usuario=self.usuario,
        )

        acoes = list(
            self.parecer.historico.order_by(
                "criado_em",
                "id",
            ).values_list(
                "acao",
                flat=True,
            )
        )

        self.assertEqual(
            acoes[:2],
            [
                "DILIGENCIA_CRIADA",
                "REANALISE_INICIADA",
            ],
        )
