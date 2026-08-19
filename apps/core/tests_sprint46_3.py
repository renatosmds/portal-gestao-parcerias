from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.pareceres.models import ItemParecer, ParecerTecnico
from apps.pareceres.services import (
    categoria_para_item,
    incorporar_resultado_regra,
    severidade_para_item,
)
from apps.prestacao.models import Prestacao
from apps.regras.resultado import ResultadoRegra


User = get_user_model()


class Sprint463ConversaoAchadosTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="analista463",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.3",
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

    def resultado_exemplo(self):
        return ResultadoRegra(
            codigo="PT_TESTE_001",
            severidade="critica",
            titulo="Execucao incompat?vel",
            descricao="Foi identificada uma inconsist?ncia.",
            regra="regra_teste",
            categoria="plano_trabalho",
            resultado="achado",
            fato_verificado="Quantidade executada superior.",
            evidencia="Item MAT-001.",
            fundamentacao="Fundamenta??o normativa de teste.",
            risco_glosa="Risco potencial de glosa.",
            recomendacao="Solicitar esclarecimentos.",
            origem_normativa="Lei Federal n? 13.019/2014",
        )

    def test_converte_resultado_em_item_parecer(self):
        resultado = self.resultado_exemplo()

        item = incorporar_resultado_regra(
            parecer=self.parecer,
            resultado=resultado,
            usuario=self.usuario,
        )

        self.assertEqual(
            item.codigo_regra,
            "PT_TESTE_001",
        )

        self.assertEqual(
            item.origem,
            ItemParecer.Origem.PGP_RULES,
        )

        self.assertEqual(
            item.severidade,
            ItemParecer.Severidade.CRITICA,
        )

        self.assertEqual(
            item.categoria,
            ItemParecer.Categoria.PLANO_TRABALHO,
        )

    def test_preserva_snapshot_do_resultado(self):
        resultado = self.resultado_exemplo()

        item = incorporar_resultado_regra(
            parecer=self.parecer,
            resultado=resultado,
            usuario=self.usuario,
        )

        self.assertEqual(
            item.dados_origem["codigo"],
            "PT_TESTE_001",
        )

        self.assertEqual(
            item.dados_origem["fato_verificado"],
            "Quantidade executada superior.",
        )

        self.assertEqual(
            item.dados_origem["origem_normativa"],
            "Lei Federal n? 13.019/2014",
        )

    def test_achado_nao_gera_decisao_automatica(self):
        item = incorporar_resultado_regra(
            parecer=self.parecer,
            resultado=self.resultado_exemplo(),
            usuario=self.usuario,
        )

        self.assertEqual(
            item.conclusao_item,
            ItemParecer.ConclusaoItem.NAO_ANALISADO,
        )

        self.assertEqual(
            item.manifestacao_analista,
            "",
        )

        self.assertEqual(
            self.parecer.situacao,
            ParecerTecnico.Situacao.RASCUNHO,
        )

        self.assertEqual(
            self.parecer.tipo_conclusao,
            ParecerTecnico.TipoConclusao.EM_ANALISE,
        )

    def test_valores_desconhecidos_usam_fallback_seguro(self):
        self.assertEqual(
            severidade_para_item("qualquer"),
            ItemParecer.Severidade.ALERTA,
        )

        self.assertEqual(
            categoria_para_item("categoria futura"),
            ItemParecer.Categoria.OUTRA,
        )

    def test_exige_usuario_responsavel(self):
        with self.assertRaises(ValidationError):
            incorporar_resultado_regra(
                parecer=self.parecer,
                resultado=self.resultado_exemplo(),
                usuario=None,
            )
