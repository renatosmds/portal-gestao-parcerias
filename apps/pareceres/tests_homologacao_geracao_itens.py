from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.documentos.models import Documento
from apps.lancamentos.models import Lancamento
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)
from apps.pareceres.services import (
    _resultados_do_motor,
    gerar_itens_iniciais_parecer,
)
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos
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
            titulo="Achado de lançamento",
        )

        achado_2 = ResultadoFake(
            codigo="LANC-002",
            severidade="critico",
            titulo="Achado crítico",
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

    @patch(
        "apps.pareceres.services."
        "motor_regras.analisar_documento"
    )
    @patch(
        "apps.pareceres.services."
        "motor_regras.analisar_lancamento"
    )
    def test_nao_mistura_prestacoes_do_mesmo_termo(
        self,
        analisar_lancamento,
        analisar_documento,
    ):
        analisar_lancamento.return_value = []
        analisar_documento.return_value = []

        termo = Termos.objects.create(
            empresa=self.empresa,
            termo="Termo de Colaboracao",
            numtermo="ESCOPO-001/2026",
        )

        prestacao_1 = Prestacao.objects.create(
            empresa=self.empresa,
            termo=termo,
            tipo="cnpj",
            numtermo="ESCOPO-001/2026-P1",
        )

        prestacao_2 = Prestacao.objects.create(
            empresa=self.empresa,
            termo=termo,
            tipo="cnpj",
            numtermo="ESCOPO-001/2026-P2",
        )

        parecer = ParecerTecnico.objects.create(
            prestacao=prestacao_1,
            empresa=self.empresa,
            numero="PT-ESCOPO-001",
            elaborado_por=self.usuario,
        )

        lancamento_1 = Lancamento.objects.create(
            empresa=self.empresa,
            termo=termo,
            prestacao=prestacao_1,
            numero_lancamento="ESCOPO-L1",
            data_documento=date(
                2026,
                1,
                10,
            ),
            descricao="Lancamento prestacao 1",
            valor_documento=Decimal("100.00"),
        )

        lancamento_2 = Lancamento.objects.create(
            empresa=self.empresa,
            termo=termo,
            prestacao=prestacao_2,
            numero_lancamento="ESCOPO-L2",
            data_documento=date(
                2026,
                2,
                10,
            ),
            descricao="Lancamento prestacao 2",
            valor_documento=Decimal("200.00"),
        )

        documento_1 = Documento.objects.create(
            empresa=self.empresa,
            termo=termo,
            prestacao=prestacao_1,
            lancamento=lancamento_1,
            descricao="Documento prestacao 1",
            arquivo=SimpleUploadedFile(
                "prestacao1.pdf",
                b"conteudo prestacao 1",
                content_type="application/pdf",
            ),
        )

        documento_2 = Documento.objects.create(
            empresa=self.empresa,
            termo=termo,
            prestacao=prestacao_2,
            lancamento=lancamento_2,
            descricao="Documento prestacao 2",
            arquivo=SimpleUploadedFile(
                "prestacao2.pdf",
                b"conteudo prestacao 2",
                content_type="application/pdf",
            ),
        )

        lancamento_legado = Lancamento.objects.create(
            empresa=self.empresa,
            termo=termo,
            prestacao=None,
            numero_lancamento="ESCOPO-LEGADO-L1",
            data_documento=date(
                2026,
                3,
                10,
            ),
            descricao="Lancamento legado sem prestacao",
            valor_documento=Decimal("50.00"),
        )

        documento_legado = Documento.objects.create(
            empresa=self.empresa,
            termo=termo,
            prestacao=None,
            lancamento=None,
            descricao="Documento legado sem prestacao",
            arquivo=SimpleUploadedFile(
                "legado.pdf",
                b"conteudo legado",
                content_type="application/pdf",
            ),
        )

        gerar_itens_iniciais_parecer(
            parecer=parecer,
            usuario=self.usuario,
        )

        lancamentos_analisados = {
            chamada.args[0].pk
            for chamada
            in analisar_lancamento.call_args_list
        }

        documentos_analisados = {
            chamada.args[0].pk
            for chamada
            in analisar_documento.call_args_list
        }

        self.assertIn(
            lancamento_1.pk,
            lancamentos_analisados,
        )

        self.assertNotIn(
            lancamento_2.pk,
            lancamentos_analisados,
        )

        self.assertIn(
            lancamento_legado.pk,
            lancamentos_analisados,
        )

        self.assertIn(
            documento_legado.pk,
            documentos_analisados,
        )

        # Documentos ligados a lancamentos sao analisados
        # no fluxo do proprio lancamento e nao novamente
        # como documento avulso.
        self.assertNotIn(
            documento_2.pk,
            documentos_analisados,
        )
