from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.pareceres.models import ItemParecer, ParecerTecnico
from apps.pareceres.textos import gerar_texto_inconformidade
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint464TextoInconformidadeTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="analista464",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.4",
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
            "codigo": "INC-001",
            "titulo": "Documento incompat?vel",
            "descricao": (
                "Foi identificada diverg?ncia documental"
            ),
            "fato_verificado": (
                "O valor informado n?o corresponde "
                "ao documento analisado"
            ),
            "evidencia": (
                "Documento fiscal vinculado ao lan?amento"
            ),
            "fundamentacao": (
                "Fundamenta??o normativa registrada "
                "na an?lise"
            ),
            "risco_glosa": (
                "A ocorr?ncia poder? exigir saneamento "
                "e avalia??o quanto ? glosa"
            ),
            "criado_por": self.usuario,
        }

        dados.update(kwargs)

        return ItemParecer.objects.create(**dados)

    def test_gera_texto_estruturado(self):
        item = self.criar_item()

        resultado = gerar_texto_inconformidade(item)

        self.assertIn(
            "Foi identificado o seguinte fato:",
            resultado.texto,
        )

        self.assertIn(
            "Evidência considerada:",
            resultado.texto,
        )

        self.assertIn(
            "Fundamentação indicada:",
            resultado.texto,
        )

        self.assertIn(
            "Risco identificado:",
            resultado.texto,
        )

        self.assertTrue(resultado.completo)

    def test_nao_inventa_fundamentacao(self):
        item = self.criar_item(
            fundamentacao="",
        )

        resultado = gerar_texto_inconformidade(item)

        self.assertNotIn(
            "Fundamentação indicada:",
            resultado.texto,
        )

        self.assertIn(
            "Fundamentação normativa não informada.",
            resultado.pendencias,
        )

        self.assertFalse(
            resultado.possui_fundamentacao
        )

    def test_identifica_fato_e_evidencia_ausentes(self):
        item = self.criar_item(
            fato_verificado="",
            evidencia="",
        )

        resultado = gerar_texto_inconformidade(item)

        self.assertIn(
            "Fato verificado não informado.",
            resultado.pendencias,
        )

        self.assertIn(
            "Evidência não informada.",
            resultado.pendencias,
        )

        self.assertFalse(resultado.completo)

    def test_geracao_nao_altera_decisao_administrativa(self):
        item = self.criar_item()

        conclusao_antes = item.conclusao_item
        parecer_antes = self.parecer.tipo_conclusao

        gerar_texto_inconformidade(item)

        item.refresh_from_db()
        self.parecer.refresh_from_db()

        self.assertEqual(
            item.conclusao_item,
            conclusao_antes,
        )

        self.assertEqual(
            self.parecer.tipo_conclusao,
            parecer_antes,
        )

        self.assertEqual(
            item.conclusao_item,
            ItemParecer.ConclusaoItem.NAO_ANALISADO,
        )

    def test_rejeita_objeto_que_nao_seja_item_parecer(self):
        with self.assertRaises(ValidationError):
            gerar_texto_inconformidade(
                object()
            )
