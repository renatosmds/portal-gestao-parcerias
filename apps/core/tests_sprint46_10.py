from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.diligencias.models import Diligencia
from apps.empresas.models import Empresa
from apps.pareceres.conclusao_executiva import (
    gerar_conclusao_executiva,
)
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint4610ConclusaoExecutivaTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="analista4610",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.10",
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
        *,
        codigo,
        conclusao,
        severidade=ItemParecer.Severidade.ALERTA,
        diligencia=None,
    ):
        return ItemParecer.objects.create(
            parecer=self.parecer,
            codigo=codigo,
            titulo=f"Item {codigo}",
            conclusao_item=conclusao,
            severidade=severidade,
            diligencia=diligencia,
            criado_por=self.usuario,
        )

    def test_sem_itens_gera_conclusao_inconclusiva(self):
        resultado = gerar_conclusao_executiva(
            self.parecer
        )

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.INCONCLUSIVO,
        )

        self.assertIn(
            "0 item(ns)",
            resultado.resumo_executivo,
        )

    def test_regulares_e_sanados_aparecem_como_aspectos_regulares(self):
        self.criar_item(
            codigo="REG-001",
            conclusao=ItemParecer.ConclusaoItem.REGULAR,
        )

        self.criar_item(
            codigo="SAN-001",
            conclusao=ItemParecer.ConclusaoItem.SANADO,
        )

        resultado = gerar_conclusao_executiva(
            self.parecer
        )

        self.assertEqual(
            len(resultado.aspectos_regulares),
            2,
        )

        self.assertEqual(
            len(resultado.pendencias_relevantes),
            0,
        )

    def test_nao_sanado_aparece_como_pendencia(self):
        self.criar_item(
            codigo="NS-001",
            conclusao=ItemParecer.ConclusaoItem.NAO_SANADO,
            severidade=ItemParecer.Severidade.CRITICA,
        )

        resultado = gerar_conclusao_executiva(
            self.parecer
        )

        self.assertEqual(
            resultado.classificacao_sugerida,
            ParecerTecnico.TipoConclusao.COM_IRREGULARIDADES,
        )

        self.assertEqual(
            len(resultado.pendencias_relevantes),
            1,
        )

        self.assertEqual(
            resultado.itens_criticos,
            1,
        )

    def test_diligencia_aberta_e_destacada(self):
        diligencia = Diligencia.objects.create(
            assunto="Dilig?ncia pendente",
            descricao="Aguardando manifesta??o da OSC.",
            empresa=self.empresa,
            prestacao=self.prestacao,
            criada_por=self.usuario,
            status=Diligencia.Status.ENVIADA,
        )

        self.criar_item(
            codigo="DIL-001",
            conclusao=ItemParecer.ConclusaoItem.PENDENCIA_SANEAVEL,
            diligencia=diligencia,
        )

        resultado = gerar_conclusao_executiva(
            self.parecer
        )

        self.assertEqual(
            resultado.diligencias_pendentes,
            1,
        )

        self.assertIn(
            "1 dilig?ncia(s)",
            resultado.resumo_executivo,
        )

    def test_contabiliza_severidades(self):
        self.criar_item(
            codigo="C-001",
            conclusao=ItemParecer.ConclusaoItem.NAO_ANALISADO,
            severidade=ItemParecer.Severidade.CRITICA,
        )

        self.criar_item(
            codigo="A-001",
            conclusao=ItemParecer.ConclusaoItem.RESSALVA,
            severidade=ItemParecer.Severidade.ALERTA,
        )

        self.criar_item(
            codigo="I-001",
            conclusao=ItemParecer.ConclusaoItem.REGULAR,
            severidade=ItemParecer.Severidade.INFORMATIVA,
        )

        resultado = gerar_conclusao_executiva(
            self.parecer
        )

        self.assertEqual(resultado.itens_criticos, 1)
        self.assertEqual(resultado.itens_alerta, 1)
        self.assertEqual(resultado.itens_informativos, 1)

    def test_conclusao_executiva_exige_revisao_humana(self):
        resultado = gerar_conclusao_executiva(
            self.parecer
        )

        self.assertTrue(
            resultado.requer_revisao_humana
        )

        self.assertIn(
            "revisada e validada",
            resultado.resumo_executivo,
        )

    def test_geracao_nao_altera_o_parecer(self):
        self.criar_item(
            codigo="IRR-001",
            conclusao=ItemParecer.ConclusaoItem.IRREGULARIDADE,
        )

        conclusao_antes = self.parecer.tipo_conclusao
        situacao_antes = self.parecer.situacao
        resumo_antes = self.parecer.resumo_executivo

        resultado = gerar_conclusao_executiva(
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

        self.assertEqual(
            self.parecer.resumo_executivo,
            resumo_antes,
        )
