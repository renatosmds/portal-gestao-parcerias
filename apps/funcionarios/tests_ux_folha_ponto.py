from pathlib import Path

from django.test import SimpleTestCase


class UXFolhaPontoTests(SimpleTestCase):

    def setUp(self):

        self.template = Path(
            "apps/funcionarios/templates/"
            "funcionarios/folha_ponto_form.html"
        ).read_text(
            encoding="utf-8"
        )

    def test_ordem_logica_botoes(self):

        preencher = self.template.index(
            'value="preencher_padrao"'
        )

        salvar = self.template.index(
            'value="salvar"'
        )

        apurar = self.template.index(
            'value="apurar"'
        )

        processar = self.template.index(
            'value="processar"'
        )

        self.assertLess(
            preencher,
            salvar,
        )

        self.assertLess(
            salvar,
            apurar,
        )

        self.assertLess(
            apurar,
            processar,
        )

    def test_tem_destaque_para_marcacao_fora_padrao(self):

        self.assertIn(
            "pgp-mark-positive",
            self.template,
        )

        self.assertIn(
            "pgp-mark-negative",
            self.template,
        )

        self.assertIn(
            "highlightMarkings",
            self.template,
        )

        self.assertIn(
            "Horário padrão:",
            self.template,
        )

    def test_tem_saldo_semantico(self):

        self.assertIn(
            "pgp-saldo-positive",
            self.template,
        )

        self.assertIn(
            "pgp-saldo-negative",
            self.template,
        )

        self.assertIn(
            "pgp-card-positive",
            self.template,
        )

        self.assertIn(
            "pgp-card-negative",
            self.template,
        )

    def test_tem_cards_de_resumo_diario(self):

        for identificador in [
            "resumo-previstas",
            "resumo-trabalhadas",
            "resumo-abonadas",
            "resumo-extras-apuradas",
            "resumo-faltas",
            "resumo-saldo",
        ]:

            self.assertIn(
                identificador,
                self.template,
            )
