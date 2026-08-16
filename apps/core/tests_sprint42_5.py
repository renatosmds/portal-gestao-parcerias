from django.test import SimpleTestCase

from apps.regras.context import ContextoRegras, FonteNormativa
from apps.regras.normativos import (
    LEI_13019_VIGENTE,
    contexto_normativo_base,
    fontes_contagem,
)


class ContextoNormativoSprint42Tests(SimpleTestCase):

    def test_lei_13019_vigente_e_nacional(self):
        self.assertEqual(
            LEI_13019_VIGENTE.escopo,
            "nacional",
        )

        self.assertIn(
            "13.019/2014",
            LEI_13019_VIGENTE.titulo,
        )

        self.assertIn(
            "vigente",
            LEI_13019_VIGENTE.titulo.lower(),
        )

        self.assertIn(
            "alterações",
            LEI_13019_VIGENTE.titulo.lower(),
        )

    def test_contexto_base_contem_lei_federal(self):
        fontes = contexto_normativo_base()

        self.assertIn(
            LEI_13019_VIGENTE,
            fontes,
        )

        self.assertEqual(
            len(fontes),
            1,
        )

    def test_normas_contagem_sao_locais(self):
        fontes = fontes_contagem()

        self.assertGreater(
            len(fontes),
            0,
        )

        for fonte in fontes:
            self.assertNotEqual(
                fonte.escopo,
                "nacional",
            )
            self.assertEqual(
                fonte.ente,
                "Contagem/MG",
            )

    def test_outro_municipio_nao_recebe_normas_contagem(self):
        norma_local_outro_municipio = FonteNormativa(
            codigo="MUNICIPIO_B_DEC_001",
            titulo="Decreto Municipal nº 001/2026",
            escopo="municipal",
            referencia="Regulamentação local do MROSC",
            ente="Município B/MG",
        )

        contexto = ContextoRegras(
            municipio="Município B/MG",
            fontes_normativas=contexto_normativo_base(
                norma_local_outro_municipio
            ),
        )

        codigos = {
            fonte.codigo
            for fonte in contexto.fontes_normativas
        }

        self.assertIn(
            "BR_LEI_13019_2014",
            codigos,
        )

        self.assertIn(
            "MUNICIPIO_B_DEC_001",
            codigos,
        )

        self.assertNotIn(
            "CONTAGEM_DEC_30_2017",
            codigos,
        )

        self.assertNotIn(
            "CONTAGEM_MANUAL_PC",
            codigos,
        )

    def test_contexto_separa_fontes_nacionais_e_locais(self):
        contexto = ContextoRegras(
            municipio="Contagem/MG",
            fontes_normativas=contexto_normativo_base(
                *fontes_contagem()
            ),
        )

        self.assertEqual(
            len(contexto.fontes_nacionais),
            1,
        )

        self.assertGreaterEqual(
            len(contexto.fontes_locais),
            2,
        )

        self.assertEqual(
            contexto.fontes_nacionais[0].codigo,
            "BR_LEI_13019_2014",
        )
