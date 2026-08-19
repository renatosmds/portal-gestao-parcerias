from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.pareceres.models import ItemParecer, ParecerTecnico
from apps.pareceres.textos import gerar_texto_recomendacao
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint465TextoRecomendacaoTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="analista465",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.5",
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

    def criar_item(self, **kwargs):
        dados = {
            "parecer": self.parecer,
            "codigo": "REC-001",
            "titulo": "Pend?ncia documental",
            "descricao": "Documento necessita esclarecimento.",
            "fato_verificado": "Documento incompleto.",
            "evidencia": "Arquivo apresentado pela OSC.",
            "fundamentacao": (
                "Fundamenta??o normativa registrada "
                "no item."
            ),
            "recomendacao": (
                "Solicitar esclarecimentos e documenta??o "
                "complementar ? OSC"
            ),
            "criado_por": self.usuario,
        }

        dados.update(kwargs)

        return ItemParecer.objects.create(**dados)

    def test_gera_recomendacao_estruturada(self):
        item = self.criar_item()

        resultado = gerar_texto_recomendacao(item)

        self.assertIn(
            "Recomenda-se:",
            resultado.texto,
        )

        self.assertIn(
            "Fundamenta??o considerada:",
            resultado.texto,
        )

        self.assertIn(
            "Evid?ncia relacionada:",
            resultado.texto,
        )

        self.assertTrue(
            resultado.completo
        )

    def test_nao_inventa_recomendacao(self):
        item = self.criar_item(
            recomendacao="",
        )

        resultado = gerar_texto_recomendacao(item)

        self.assertIn(
            "Recomenda??o t?cnica n?o informada.",
            resultado.pendencias,
        )

        self.assertFalse(
            resultado.possui_recomendacao
        )

        self.assertIn(
            "an?lise t?cnica complementar",
            resultado.texto,
        )

    def test_nao_inventa_fundamentacao(self):
        item = self.criar_item(
            fundamentacao="",
        )

        resultado = gerar_texto_recomendacao(item)

        self.assertNotIn(
            "Fundamenta??o considerada:",
            resultado.texto,
        )

        self.assertIn(
            "Fundamenta??o normativa n?o informada.",
            resultado.pendencias,
        )

        self.assertFalse(
            resultado.completo
        )

    def test_recomendacao_exige_revisao_humana(self):
        item = self.criar_item()

        resultado = gerar_texto_recomendacao(item)

        self.assertTrue(
            resultado.requer_revisao_humana
        )

        self.assertIn(
            "dever? ser validada pelo analista respons?vel",
            resultado.texto,
        )

    def test_geracao_nao_altera_item_ou_parecer(self):
        item = self.criar_item()

        conclusao_item_antes = item.conclusao_item
        conclusao_parecer_antes = self.parecer.tipo_conclusao

        gerar_texto_recomendacao(item)

        item.refresh_from_db()
        self.parecer.refresh_from_db()

        self.assertEqual(
            item.conclusao_item,
            conclusao_item_antes,
        )

        self.assertEqual(
            self.parecer.tipo_conclusao,
            conclusao_parecer_antes,
        )

        self.assertEqual(
            item.conclusao_item,
            ItemParecer.ConclusaoItem.NAO_ANALISADO,
        )

    def test_rejeita_objeto_invalido(self):
        with self.assertRaises(ValidationError):
            gerar_texto_recomendacao(
                object()
            )
