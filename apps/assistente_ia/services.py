from datetime import datetime

from django.db.models import Q

from apps.documentos.models import Documento


def _parse_data(valor):
    if not valor:
        return None
    if hasattr(valor, "year"):
        return valor
    texto = str(valor).strip()
    for formato in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


def validar_documento(documento):
    """
    Compatibilidade com a interface existente do Assistente IA.

    As regras deterministicas agora sao executadas pelo PGP Rules.
    """
    from apps.regras.engine import motor_regras

    return [
        resultado.como_dict()
        for resultado in motor_regras.analisar_documento(documento)
    ]

def gerar_rascunhos(documento, achados):
    relevantes = [a for a in achados if a["severidade"] in {"alerta", "critico"}]
    resumo = (
        f"Foram executadas validaÃ§Ãµes locais no documento â€œ{documento}â€. "
        f"Foram identificados {len(relevantes)} ponto(s) que exigem conferÃªncia humana."
    )
    if not relevantes:
        return {
            "resumo": resumo,
            "inconformidade": "",
            "diligencia": "",
            "recomendacao": "Manter a conferÃªncia documental e financeira antes da decisÃ£o final.",
        }

    itens = "; ".join(a["titulo"].lower() for a in relevantes)
    return {
        "resumo": resumo,
        "inconformidade": (
            "Na anÃ¡lise preliminar assistida foram identificados os seguintes pontos: "
            f"{itens}. Os apontamentos devem ser confirmados pelo analista antes de qualquer conclusÃ£o."
        ),
        "diligencia": (
            "Solicita-se Ã  OSC que apresente esclarecimentos e, quando aplicÃ¡vel, documentaÃ§Ã£o complementar "
            f"para sanar os seguintes pontos: {itens}."
        ),
        "recomendacao": (
            "Recomenda-se conferir os documentos vinculados, os dados do lanÃ§amento, a comprovaÃ§Ã£o do pagamento "
            "e a compatibilidade com a vigÃªncia e o objeto da parceria."
        ),
    }

