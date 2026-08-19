from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.diligencias.models import Diligencia
from apps.empresas.models import Empresa
from apps.pareceres.classificacao import (
    classificar_parecer_tecnicamente,
)
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint468ClassificacaoParecerTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="analista468",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.8",
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

    def criar_item(
        self,
        conclusao=ItemParecer.ConclusaoItem.NAO_ANALISADO,
        codigo="ITEM-001",
        diligencia=None,
    ):
        return ItemParecer.objects.create(
            parecer=self.parecer,
            codigo=codigo,
            titulo="Item de teste",
            conclusao_item=conclusao,
            diligencia=diligencia,
            criado_por=self.usuario,
        )

    def test_sem_itens_resulta_inconclusivo(self):
        resultado = classificar_parecer_tecnicamente(
            self.parecer
        )

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.INCONCLUSIVO,
        )

    def test_item_nao_analisado_mantem_em_analise(self):
        self.criar_item()

        resultado = classificar_parecer_tecnicamente(
            self.parecer
        )

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.EM_ANALISE,
        )

    def test_itens_regulares_e_sanados_sem_pendencias(self):
        self.criar_item(
            ItemParecer.ConclusaoItem.REGULAR,
            "REG-001",
        )

        self.criar_item(
            ItemParecer.ConclusaoItem.SANADO,
            "SAN-001",
        )

        resultado = classificar_parecer_tecnicamente(
            self.parecer
        )

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.SEM_PENDENCIAS_RELEVANTES,
        )

    def test_ressalva_resulta_com_ressalvas(self):
        self.criar_item(
            ItemParecer.ConclusaoItem.RESSALVA,
        )

        resultado = classificar_parecer_tecnicamente(
            self.parecer
        )

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.COM_RESSALVAS,
        )

    def test_pendencia_saneavel_tem_precedencia_sobre_ressalva(self):
        self.criar_item(
            ItemParecer.ConclusaoItem.RESSALVA,
            "RES-001",
        )

        self.criar_item(
            ItemParecer.ConclusaoItem.PENDENCIA_SANEAVEL,
            "PEN-001",
        )

        resultado = classificar_parecer_tecnicamente(
            self.parecer
        )

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.COM_PENDENCIAS_SANEAVEIS,
        )

    def test_diligencia_aberta_resulta_aguardando_diligencia(self):
        diligencia = Diligencia.objects.create(
            assunto="Diligencia aberta",
            descricao="Aguardando resposta.",
            empresa=self.empresa,
            prestacao=self.prestacao,
            criada_por=self.usuario,
            status=Diligencia.Status.ENVIADA,
        )

        self.criar_item(
            ItemParecer.ConclusaoItem.PENDENCIA_SANEAVEL,
            "DIL-001",
            diligencia=diligencia,
        )

        resultado = classificar_parecer_tecnicamente(
            self.parecer
        )

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.AGUARDANDO_DILIGENCIA,
        )

        self.assertEqual(
            resultado.diligencias_abertas,
            1,
        )

    def test_nao_sanado_tem_maior_precedencia(self):
        diligencia = Diligencia.objects.create(
            assunto="Outra diligencia",
            descricao="Em andamento.",
            empresa=self.empresa,
            prestacao=self.prestacao,
            criada_por=self.usuario,
            status=Diligencia.Status.REANALISE,
        )

        self.criar_item(
            ItemParecer.ConclusaoItem.PENDENCIA_SANEAVEL,
            "PEN-001",
            diligencia=diligencia,
        )

        self.criar_item(
            ItemParecer.ConclusaoItem.NAO_SANADO,
            "NS-001",
        )

        resultado = classificar_parecer_tecnicamente(
            self.parecer
        )

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.COM_IRREGULARIDADES,
        )

    def test_classificacao_nao_altera_parecer(self):
        self.criar_item(
            ItemParecer.ConclusaoItem.NAO_SANADO,
        )

        conclusao_antes = self.parecer.tipo_conclusao
        situacao_antes = self.parecer.situacao

        resultado = classificar_parecer_tecnicamente(
            self.parecer
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.COM_IRREGULARIDADES,
        )

        self.assertEqual(
            self.parecer.tipo_conclusao,
            conclusao_antes,
        )

        self.assertEqual(
            self.parecer.situacao,
            situacao_antes,
        )

        self.assertTrue(
            resultado.requer_revisao_humana
        )
