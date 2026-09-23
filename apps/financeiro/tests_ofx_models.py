from django.test import SimpleTestCase

from apps.financeiro.models import (
    ImportacaoOFX,
    MovimentacaoFinanceira,
)


class EstruturaOFXTests(SimpleTestCase):

    def test_importacao_ofx_existe(self):
        campos = {
            campo.name
            for campo
            in ImportacaoOFX._meta.get_fields()
        }

        esperados = {
            "empresa",
            "termo",
            "prestacao",
            "nome_arquivo",
            "hash_arquivo",
            "banco",
            "conta_mascarada",
            "tipo_conta",
            "moeda",
            "data_inicio",
            "data_fim",
            "saldo_informado",
            "data_saldo",
            "quantidade_movimentos",
            "importado_por",
            "importado_em",
        }

        self.assertTrue(
            esperados.issubset(campos)
        )

    def test_movimentacao_guarda_origem_ofx(self):
        campos = {
            campo.name
            for campo
            in MovimentacaoFinanceira
            ._meta
            .get_fields()
        }

        esperados = {
            "importacao_ofx",
            "ordem_ofx",
            "tipo_ofx",
            "data_hora_ofx",
            "valor_ofx",
            "fitid",
            "checknum",
            "memo_ofx",
        }

        self.assertTrue(
            esperados.issubset(campos)
        )

    def test_fitid_nao_e_unico(self):
        campo = (
            MovimentacaoFinanceira
            ._meta
            .get_field("fitid")
        )

        self.assertFalse(
            campo.unique
        )

    def test_importacao_pode_ter_prestacao_opcional(self):
        campo = (
            ImportacaoOFX
            ._meta
            .get_field("prestacao")
        )

        self.assertTrue(
            campo.null
        )

        self.assertTrue(
            campo.blank
        )

    def test_movimento_manual_nao_exige_importacao_ofx(self):
        campo = (
            MovimentacaoFinanceira
            ._meta
            .get_field("importacao_ofx")
        )

        self.assertTrue(
            campo.null
        )

        self.assertTrue(
            campo.blank
        )
