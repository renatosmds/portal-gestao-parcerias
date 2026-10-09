from datetime import date
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from apps.assistente_ia.services import (
    gerar_rascunhos_assistidos,
)

from apps.assistente_ia.services_openai import (
    IAExternaIndisponivel,
    gerar_rascunhos_openai,
    ia_externa_configurada,
    montar_contexto_minimizado,
)


class DocumentoFake:
    tipo = "nota_fiscal"
    numero_documento = "NF-001"
    data_documento = date(2026, 7, 1)
    descricao = "Nota fiscal teste"

    def get_tipo_display(self):
        return "Nota fiscal"


class AssistenteIAOpenAITests(SimpleTestCase):


    @override_settings(
        PGP_IA_ANONIMIZAR=True,
    )
    def test_anonimizacao_mascara_identificadores(self):
        documento = DocumentoFake()
        documento.descricao = (
            "Contato teste@example.com CPF 123.456.789-00 "
            "CNPJ 12.345.678/0001-90"
        )

        contexto = montar_contexto_minimizado(
            documento,
            [
                {
                    "codigo": "TESTE",
                    "severidade": "alerta",
                    "titulo": "CPF 123.456.789-00",
                    "descricao": (
                        "Enviar para teste@example.com"
                    ),
                }
            ],
        )

        serializado = str(contexto)

        self.assertNotIn(
            "123.456.789-00",
            serializado,
        )
        self.assertNotIn(
            "12.345.678/0001-90",
            serializado,
        )
        self.assertNotIn(
            "teste@example.com",
            serializado,
        )
        self.assertIn("[CPF]", serializado)
        self.assertIn("[CNPJ]", serializado)
        self.assertIn("[EMAIL]", serializado)
    @override_settings(
        PGP_IA_ATIVA=False,
        OPENAI_API_KEY="",
        PGP_IA_MODELO="",
    )
    def test_ia_externa_desativada(self):
        self.assertFalse(
            ia_externa_configurada()
        )

    @override_settings(
        PGP_IA_ATIVA=False,
        OPENAI_API_KEY="",
        PGP_IA_MODELO="",
    )
    def test_geracao_recusa_sem_configuracao(self):
        with self.assertRaises(
            IAExternaIndisponivel
        ):
            gerar_rascunhos_openai(
                DocumentoFake(),
                [],
            )

    @override_settings(
        PGP_IA_ANONIMIZAR=True,
    )
    def test_contexto_minimizado_nao_leva_empresa(self):
        contexto = montar_contexto_minimizado(
            DocumentoFake(),
            [
                {
                    "codigo": "SEM_LANCAMENTO",
                    "severidade": "alerta",
                    "titulo": "Sem lancamento",
                    "descricao": "Documento sem lancamento.",
                }
            ],
        )

        self.assertNotIn(
            "empresa",
            contexto["documento"],
        )

        self.assertEqual(
            contexto["achados"][0]["codigo"],
            "SEM_LANCAMENTO",
        )

    @override_settings(
        PGP_IA_ATIVA=True,
        OPENAI_API_KEY="teste",
        PGP_IA_MODELO="modelo-teste",
        PGP_IA_ANONIMIZAR=True,
    )
    @patch("openai.OpenAI")
    def test_geracao_usa_resposta_estruturada(
        self,
        openai_mock,
    ):
        resposta = Mock()
        resposta.output_text = (
            '{"resumo":"Resumo",'
            '"inconformidade":"Inconformidade",'
            '"diligencia":"Diligencia",'
            '"recomendacao":"Recomendacao"}'
        )

        cliente = Mock()
        cliente.responses.create.return_value = (
            resposta
        )

        openai_mock.return_value = cliente

        resultado = gerar_rascunhos_openai(
            DocumentoFake(),
            [
                {
                    "codigo": "SEM_LANCAMENTO",
                    "severidade": "alerta",
                    "titulo": "Sem lancamento",
                    "descricao": "Documento sem lancamento.",
                }
            ],
        )

        self.assertEqual(
            resultado["resumo"],
            "Resumo",
        )

        cliente.responses.create.assert_called_once()

        chamada = (
            cliente.responses
            .create
            .call_args
            .kwargs
        )

        self.assertEqual(
            chamada["model"],
            "modelo-teste",
        )

        self.assertEqual(
            chamada["text"]["format"]["type"],
            "json_schema",
        )

    @override_settings(
        PGP_IA_ATIVA=False,
        OPENAI_API_KEY="",
        PGP_IA_MODELO="",
    )
    def test_fallback_local_quando_ia_desativada(self):
        resultado, usou_externa = (
            gerar_rascunhos_assistidos(
                DocumentoFake(),
                [],
            )
        )

        self.assertFalse(usou_externa)
        self.assertIn("resumo", resultado)
        self.assertIn("recomendacao", resultado)

    @override_settings(
        PGP_IA_ATIVA=True,
        OPENAI_API_KEY="teste",
        PGP_IA_MODELO="modelo-teste",
    )
    @patch(
        "apps.assistente_ia.services_openai."
        "gerar_rascunhos_openai"
    )
    def test_fallback_local_quando_ia_falha(
        self,
        gerar_mock,
    ):
        gerar_mock.side_effect = RuntimeError(
            "falha simulada"
        )

        resultado, usou_externa = (
            gerar_rascunhos_assistidos(
                DocumentoFake(),
                [],
            )
        )

        self.assertFalse(usou_externa)
        self.assertIn("resumo", resultado)

    @override_settings(
        PGP_IA_ATIVA=True,
        OPENAI_API_KEY="teste",
        PGP_IA_MODELO="modelo-teste",
    )
    @patch(
        "apps.assistente_ia.services_openai."
        "gerar_rascunhos_openai"
    )
    def test_marca_quando_ia_externa_e_usada(
        self,
        gerar_mock,
    ):
        gerar_mock.return_value = {
            "resumo": "Resumo IA",
            "inconformidade": "Inconformidade IA",
            "diligencia": "Diligencia IA",
            "recomendacao": "Recomendacao IA",
        }

        resultado, usou_externa = (
            gerar_rascunhos_assistidos(
                DocumentoFake(),
                [],
            )
        )

        self.assertTrue(usou_externa)
        self.assertEqual(
            resultado["resumo"],
            "Resumo IA",
        )
