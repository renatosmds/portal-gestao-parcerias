from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.pareceres.models import ItemParecer, ParecerTecnico
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint462ParecerTecnicoTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="analista46",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46",
        )

        self.outra_empresa = Empresa.objects.create(
            nome="Outra OSC Sprint 46",
        )

        self.prestacao = Prestacao.objects.create(
            tipo="MENSAL",
            empresa=self.empresa,
        )

    def test_cria_parecer_estruturado(self):
        parecer = ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            elaborado_por=self.usuario,
        )

        self.assertEqual(
            parecer.situacao,
            ParecerTecnico.Situacao.RASCUNHO,
        )

        self.assertEqual(
            parecer.tipo_conclusao,
            ParecerTecnico.TipoConclusao.EM_ANALISE,
        )

    def test_empresa_do_parecer_deve_ser_compativel(self):
        parecer = ParecerTecnico(
            prestacao=self.prestacao,
            empresa=self.outra_empresa,
            elaborado_por=self.usuario,
        )

        with self.assertRaises(ValidationError):
            parecer.full_clean()

    def test_versao_deve_ser_unica_por_prestacao(self):
        ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            elaborado_por=self.usuario,
            versao=1,
        )

        segundo = ParecerTecnico(
            prestacao=self.prestacao,
            empresa=self.empresa,
            elaborado_por=self.usuario,
            versao=1,
        )

        with self.assertRaises(ValidationError):
            segundo.full_clean()

    def test_item_guarda_snapshot_do_achado(self):
        parecer = ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            elaborado_por=self.usuario,
        )

        item = ItemParecer.objects.create(
            parecer=parecer,
            codigo="PT-001",
            codigo_regra="PT_EXEC_PERIODO_COMPATIVEL",
            categoria=ItemParecer.Categoria.PLANO_TRABALHO,
            severidade=ItemParecer.Severidade.INFORMATIVA,
            origem=ItemParecer.Origem.PGP_RULES,
            titulo="Execucao temporal compativel",
            fato_verificado="Despesa dentro do periodo.",
            evidencia="Lancamento analisado.",
            fundamentacao="Regra aplicavel.",
            recomendacao="Manter registro.",
            dados_origem={
                "codigo": "PT_EXEC_PERIODO_COMPATIVEL",
                "resultado": "achado",
            },
            criado_por=self.usuario,
        )

        self.assertEqual(
            item.dados_origem["codigo"],
            "PT_EXEC_PERIODO_COMPATIVEL",
        )

        self.assertEqual(
            item.origem,
            ItemParecer.Origem.PGP_RULES,
        )
