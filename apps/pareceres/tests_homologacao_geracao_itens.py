from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)
from apps.pareceres.services import (
    _resultados_do_motor,
    gerar_itens_iniciais_parecer,
)
from apps.prestacao.models import Prestacao
from apps.regras.lancamentos import ResultadoAnaliseLancamento


class ResultadoFake:

    def __init__(
        self,
        *,
        codigo,
        severidade,
        titulo,
    ):
        self.codigo = codigo
        self.severidade = severidade
        self.titulo = titulo

    def como_dict(self):
        return {
            "codigo": self.codigo,
            "severidade": self.severidade,
            "titulo": self.titulo,
            "descricao": "Descricao de teste.",
            "categoria": "documental",
            "resultado": "ACHADO",
            "fato_verificado": "Fato de teste.",
            "evidencia": "",
            "fundamentacao": "",
            "risco_glosa": "",
            "recomendacao": "Revisar.",
            "origem_normativa": "",
        }


class GeracaoItensParecerTests(TestCase):

    def setUp(self):

        User = get_user_model()

        self.usuario = User.objects.create_superuser(
            username="gerador_itens_parecer",
            email="gerador@example.test",
            password="teste12345",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Geracao Itens Parecer",
        )

        self.prestacao = Prestacao.objects.create(
            tipo="MENSAL",
            empresa=self.empresa,
            numtermo="GERA-ITENS/2026",
        )

        self.parecer = ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            numero="PT-GERA-ITENS",
            elaborado_por=self.usuario,
        )

    @patch(
        "apps.pareceres.services."
        "motor_regras.analisar_documento"
    )
    @patch(
        "apps.pareceres.services."
        "motor_regras.analisar_lancamento"
    )
    def test_sem_achados_cria_item_informativo(
        self,
        analisar_lancamento,
        analisar_documento,
    ):

        analisar_lancamento.return_value = []
        analisar_documento.return_value = []

        total = gerar_itens_iniciais_parecer(
            parecer=self.parecer,
            usuario=self.usuario,
        )

        self.assertEqual(
            total,
            1,
        )

        item = self.parecer.itens.get()

        self.assertEqual(
            item.severidade,
            ItemParecer.Severidade.INFORMATIVA,
        )

        self.assertEqual(
            item.conclusao_item,
            ItemParecer.ConclusaoItem.NAO_ANALISADO,
        )

        self.assertEqual(
            item.origem,
            ItemParecer.Origem.PGP_RULES,
        )

    @patch(
        "apps.pareceres.services."
        "motor_regras.analisar_documento"
    )
    @patch(
        "apps.pareceres.services."
        "motor_regras.analisar_lancamento"
    )
    def test_resultado_informativo_nao_vira_achado(
        self,
        analisar_lancamento,
        analisar_documento,
    ):

        analisar_lancamento.return_value = [
            ResultadoFake(
                codigo="INFO-001",
                severidade="informativa",
                titulo="Resultado informativo",
            ),
        ]

        analisar_documento.return_value = []

        gerar_itens_iniciais_parecer(
            parecer=self.parecer,
            usuario=self.usuario,
        )

        self.assertFalse(
            self.parecer.itens.filter(
                codigo_regra="INFO-001",
            ).exists()
        )

        self.assertEqual(
            self.parecer.itens.count(),
            1,
        )

    @patch(
        "apps.pareceres.services."
        "motor_regras.analisar_documento"
    )
    @patch(
        "apps.pareceres.services."
        "motor_regras.analisar_lancamento"
    )
    def test_servico_nao_duplica_itens(
        self,
        analisar_lancamento,
        analisar_documento,
    ):

        analisar_lancamento.return_value = []
        analisar_documento.return_value = []

        gerar_itens_iniciais_parecer(
            parecer=self.parecer,
            usuario=self.usuario,
        )

        gerar_itens_iniciais_parecer(
            parecer=self.parecer,
            usuario=self.usuario,
        )

        self.assertEqual(
            self.parecer.itens.count(),
            1,
        )


    def test_resultado_analise_lancamento_expoe_achados(self):

        achado_1 = ResultadoFake(
            codigo="LANC-001",
            severidade="alerta",
            titulo="Achado de lan?amento",
        )

        achado_2 = ResultadoFake(
            codigo="LANC-002",
            severidade="critico",
            titulo="Achado cr?tico",
        )

        resultado = ResultadoAnaliseLancamento(
            lancamento_id=99,
            numero_lancamento="TESTE-99",
            achados=[
                achado_1,
                achado_2,
            ],
        )

        normalizados = _resultados_do_motor(
            resultado
        )

        self.assertEqual(
            len(normalizados),
            2,
        )

        self.assertEqual(
            normalizados[0].codigo,
            "LANC-001",
        )

        self.assertEqual(
            normalizados[1].codigo,
            "LANC-002",
        )
