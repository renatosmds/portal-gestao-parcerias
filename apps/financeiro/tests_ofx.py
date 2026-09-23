from pathlib import Path
from decimal import Decimal

from django.test import SimpleTestCase

from apps.financeiro.ofx import (
    parse_ofx,
)


class ParserOFXTests(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.fixture = (
            Path(__file__).resolve().parent
            / "tests"
            / "fixtures"
            / "ofx"
            / "extrato_referencia_julho_2026.ofx"
        )

        cls.extrato = parse_ofx(
            cls.fixture
        )

    def test_metadados_do_extrato(self):
        self.assertEqual(
            self.extrato.versao,
            "102",
        )

        self.assertEqual(
            self.extrato.charset,
            "1252",
        )

        self.assertEqual(
            self.extrato.moeda,
            "BRL",
        )

        self.assertEqual(
            self.extrato.banco,
            "0104",
        )

        self.assertEqual(
            self.extrato.conta,
            "0000000000000",
        )

        self.assertEqual(
            self.extrato.tipo_conta,
            "CHECKING",
        )

        self.assertEqual(
            self.extrato.data_inicio,
            "20260701",
        )

        self.assertEqual(
            self.extrato.data_fim,
            "20260731",
        )

    def test_quantidade_movimentos(self):
        self.assertEqual(
            len(
                self.extrato.movimentos
            ),
            103,
        )

    def test_primeiro_movimento(self):
        movimento = (
            self.extrato.movimentos[0]
        )

        self.assertEqual(
            movimento.tipo,
            "DEBIT",
        )

        self.assertEqual(
            movimento.valor,
            Decimal("-4562.61"),
        )

        self.assertEqual(
            movimento.fitid,
            "11035",
        )

        self.assertEqual(
            movimento.checknum,
            "11035",
        )

        self.assertEqual(
            movimento.memo,
            "ENVIO TEV",
        )

        self.assertEqual(
            movimento.data_postagem.year,
            2026,
        )

        self.assertEqual(
            movimento.data_postagem.month,
            7,
        )

        self.assertEqual(
            movimento.data_postagem.day,
            1,
        )

    def test_fitid_zero_pode_repetir(self):
        movimentos = [
            m
            for m
            in self.extrato.movimentos
            if m.fitid == "0"
        ]

        self.assertEqual(
            len(movimentos),
            17,
        )

    def test_resgates_automaticos(self):
        movimentos = [
            m
            for m
            in self.extrato.movimentos
            if m.memo == "RESG AUT"
        ]

        self.assertEqual(
            len(movimentos),
            17,
        )

    def test_estornos_ted(self):
        movimentos = [
            m
            for m
            in self.extrato.movimentos
            if m.memo == "ES.ENV.TED"
        ]

        self.assertEqual(
            len(movimentos),
            2,
        )

    def test_devolucao_ted(self):
        movimentos = [
            m
            for m
            in self.extrato.movimentos
            if m.memo == "DEV. TED"
        ]

        self.assertEqual(
            len(movimentos),
            1,
        )

    def test_fitid_nao_e_unico(self):
        fitids = [
            m.fitid
            for m
            in self.extrato.movimentos
        ]

        self.assertLess(
            len(set(fitids)),
            len(fitids),
        )

    def test_saldo_informado(self):
        self.assertEqual(
            self.extrato.saldo,
            Decimal("1135860.09"),
        )

        self.assertEqual(
            self.extrato.data_saldo,
            "20260811",
        )
