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
    achados = []

    def add(codigo, severidade, titulo, descricao):
        achados.append(
            {
                "codigo": codigo,
                "severidade": severidade,
                "titulo": titulo,
                "descricao": descricao,
            }
        )

    if not documento.lancamento_id:
        add(
            "SEM_LANCAMENTO",
            "critico",
            "Documento sem lançamento vinculado",
            "O documento não está associado a um lançamento financeiro, o que impede a conferência integrada.",
        )

    if not documento.documento_legivel:
        add(
            "NAO_LEGIVEL",
            "alerta",
            "Legibilidade ainda não confirmada",
            "O checklist do documento não registra confirmação de que o arquivo está legível.",
        )

    if not documento.dados_compativeis:
        add(
            "DADOS_NAO_COMPATIVEIS",
            "alerta",
            "Compatibilidade dos dados não confirmada",
            "Os dados do documento ainda não foram marcados como compatíveis com os dados cadastrados.",
        )

    if documento.tipo in {
        Documento.Tipo.NOTA_FISCAL,
        Documento.Tipo.FOLHA,
        Documento.Tipo.GUIA,
    } and not documento.pagamento_comprovado:
        add(
            "SEM_COMPROVANTE_PAGAMENTO",
            "critico",
            "Pagamento não comprovado",
            "Não há confirmação de comprovante de pagamento para este documento.",
        )

    if documento.termo_id and not documento.vigencia_valida:
        add(
            "VIGENCIA_NAO_CONFIRMADA",
            "alerta",
            "Vigência ainda não validada",
            "O checklist não confirma que a data do documento está dentro da vigência do Termo.",
        )

    if documento.tipo == Documento.Tipo.NOTA_FISCAL and not documento.atesto_valido:
        add(
            "ATESTO_NAO_CONFIRMADO",
            "alerta",
            "Atesto não confirmado",
            "O documento fiscal ainda não possui confirmação de atesto válido.",
        )

    lancamento = documento.lancamento
    if lancamento:
        if (
            documento.numero_documento
            and lancamento.numero_documento
            and documento.numero_documento.strip().lower()
            != lancamento.numero_documento.strip().lower()
        ):
            add(
                "NUMERO_DIVERGENTE",
                "critico",
                "Número do documento divergente",
                f"Documento: {documento.numero_documento}. Lançamento: {lancamento.numero_documento}.",
            )

        if (
            documento.data_documento
            and lancamento.data_documento
            and documento.data_documento != lancamento.data_documento
        ):
            add(
                "DATA_DIVERGENTE",
                "alerta",
                "Data do documento divergente",
                f"Documento: {documento.data_documento:%d/%m/%Y}. Lançamento: {lancamento.data_documento:%d/%m/%Y}.",
            )

        if not lancamento.data_pagamento:
            add(
                "LANCAMENTO_SEM_DATA_PAGAMENTO",
                "alerta",
                "Lançamento sem data de pagamento",
                "O lançamento vinculado não possui data de pagamento informada.",
            )

        if lancamento.tipo_glosa != lancamento.TipoGlosa.NENHUMA:
            add(
                "GLOSA_EXISTENTE",
                "info",
                "Lançamento já possui glosa",
                f"Tipo: {lancamento.get_tipo_glosa_display()}. Valor: R$ {lancamento.valor_glosa}.",
            )

    if documento.numero_documento:
        duplicados = Documento.objects.filter(
            empresa=documento.empresa,
            numero_documento__iexact=documento.numero_documento.strip(),
        ).exclude(pk=documento.pk)
        if documento.data_documento:
            duplicados = duplicados.filter(data_documento=documento.data_documento)
        if duplicados.exists():
            add(
                "POSSIVEL_DUPLICIDADE",
                "critico",
                "Possível documento duplicado",
                "Foi localizado outro documento da mesma OSC com o mesmo número e data.",
            )

    termo = documento.termo
    if termo and documento.data_documento:
        inicio = _parse_data(getattr(termo, "inicioVigencia", None))
        fim = _parse_data(getattr(termo, "terminoVigencia", None))
        if inicio and documento.data_documento < inicio:
            add(
                "ANTES_DA_VIGENCIA",
                "critico",
                "Documento anterior à vigência",
                f"A data do documento é anterior ao início da vigência ({inicio:%d/%m/%Y}).",
            )
        if fim and documento.data_documento > fim:
            add(
                "APOS_A_VIGENCIA",
                "critico",
                "Documento posterior à vigência",
                f"A data do documento é posterior ao fim da vigência ({fim:%d/%m/%Y}).",
            )

    if not achados:
        add(
            "SEM_INCONSISTENCIA_LOCAL",
            "info",
            "Nenhuma inconsistência local identificada",
            "As validações automáticas disponíveis não localizaram divergências. A revisão humana continua obrigatória.",
        )

    return achados


def gerar_rascunhos(documento, achados):
    relevantes = [a for a in achados if a["severidade"] in {"alerta", "critico"}]
    resumo = (
        f"Foram executadas validações locais no documento “{documento}”. "
        f"Foram identificados {len(relevantes)} ponto(s) que exigem conferência humana."
    )
    if not relevantes:
        return {
            "resumo": resumo,
            "inconformidade": "",
            "diligencia": "",
            "recomendacao": "Manter a conferência documental e financeira antes da decisão final.",
        }

    itens = "; ".join(a["titulo"].lower() for a in relevantes)
    return {
        "resumo": resumo,
        "inconformidade": (
            "Na análise preliminar assistida foram identificados os seguintes pontos: "
            f"{itens}. Os apontamentos devem ser confirmados pelo analista antes de qualquer conclusão."
        ),
        "diligencia": (
            "Solicita-se à OSC que apresente esclarecimentos e, quando aplicável, documentação complementar "
            f"para sanar os seguintes pontos: {itens}."
        ),
        "recomendacao": (
            "Recomenda-se conferir os documentos vinculados, os dados do lançamento, a comprovação do pagamento "
            "e a compatibilidade com a vigência e o objeto da parceria."
        ),
    }
