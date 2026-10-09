import json
import re

from django.conf import settings


class IAExternaIndisponivel(Exception):
    """IA externa nao configurada ou temporariamente indisponivel."""


def ia_externa_configurada():
    return bool(
        settings.PGP_IA_ATIVA
        and settings.OPENAI_API_KEY
        and settings.PGP_IA_MODELO
    )


def anonimizar_texto(valor):
    """
    Mascaramento preventivo de identificadores comuns.

    Nao pretende substituir processo formal de anonimiza??o
    ou revis?o humana de dados pessoais.
    """
    texto = str(valor or "")

    texto = re.sub(
        r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL]",
        texto,
    )

    texto = re.sub(
        r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
        "[CPF]",
        texto,
    )

    texto = re.sub(
        r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
        "[CNPJ]",
        texto,
    )

    return texto


def montar_contexto_minimizado(documento, achados):
    """
    Monta somente o contexto necessario para a IA redacional.

    O motor deterministico do PGP continua sendo a fonte
    dos achados. A IA nao decide aprovacao ou reprovacao.
    """
    dados = {
        "documento": {
            "tipo": (
                documento.get_tipo_display()
                if hasattr(documento, "get_tipo_display")
                else str(getattr(documento, "tipo", ""))
            ),
            "numero": getattr(
                documento,
                "numero_documento",
                "",
            ),
            "data": (
                str(documento.data_documento)
                if getattr(
                    documento,
                    "data_documento",
                    None,
                )
                else ""
            ),
            "descricao": getattr(
                documento,
                "descricao",
                "",
            ),
        },
        "achados": [
            {
                "codigo": item.get("codigo", ""),
                "severidade": item.get(
                    "severidade",
                    "",
                ),
                "titulo": item.get(
                    "titulo",
                    "",
                ),
                "descricao": item.get(
                    "descricao",
                    "",
                ),
            }
            for item in achados
        ],
    }

    if settings.PGP_IA_ANONIMIZAR:
        dados["documento"]["numero"] = anonimizar_texto(
            dados["documento"]["numero"]
        )
        dados["documento"]["descricao"] = anonimizar_texto(
            dados["documento"]["descricao"]
        )

        for item in dados["achados"]:
            item["titulo"] = anonimizar_texto(
                item["titulo"]
            )
            item["descricao"] = anonimizar_texto(
                item["descricao"]
            )

    return dados


def _schema_saida():
    return {
        "type": "object",
        "properties": {
            "resumo": {
                "type": "string",
            },
            "inconformidade": {
                "type": "string",
            },
            "diligencia": {
                "type": "string",
            },
            "recomendacao": {
                "type": "string",
            },
        },
        "required": [
            "resumo",
            "inconformidade",
            "diligencia",
            "recomendacao",
        ],
        "additionalProperties": False,
    }


def gerar_rascunhos_openai(documento, achados):
    """
    Gera rascunhos com IA externa.

    A IA recebe achados previamente produzidos pelo
    motor deterministico e nao toma decisao administrativa.
    """
    if not ia_externa_configurada():
        raise IAExternaIndisponivel(
            "IA externa nao esta configurada."
        )

    from openai import OpenAI

    cliente = OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )

    contexto = montar_contexto_minimizado(
        documento,
        achados,
    )

    instrucoes = """
Voce e um assistente de apoio a analise de prestacao de
contas de parcerias publicas.

Utilize exclusivamente os dados fornecidos.

Nao crie fatos, documentos, valores ou fundamentos
normativos inexistentes.

Os achados foram produzidos pelo motor deterministico
do sistema PGP e devem ser tratados como pontos sujeitos
a conferencia humana.

Nao decida aprovacao, rejeicao, glosa ou responsabilizacao.

Produza textos tecnicos, objetivos e prudentes para:
1. resumo;
2. inconformidade;
3. diligencia;
4. recomendacao.

Deixe claro quando algo depender de conferencia humana.
""".strip()

    resposta = cliente.responses.create(
        model=settings.PGP_IA_MODELO,
        instructions=instrucoes,
        input=json.dumps(
            contexto,
            ensure_ascii=False,
        ),
        text={
            "format": {
                "type": "json_schema",
                "name": "rascunho_analise_pgp",
                "strict": True,
                "schema": _schema_saida(),
            }
        },
    )

    texto = resposta.output_text

    if not texto:
        raise IAExternaIndisponivel(
            "A IA externa retornou resposta vazia."
        )

    try:
        resultado = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise IAExternaIndisponivel(
            "A IA externa retornou JSON invalido."
        ) from exc

    return resultado
