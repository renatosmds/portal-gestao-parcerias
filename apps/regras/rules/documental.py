from datetime import datetime

from apps.documentos.models import Documento
from apps.regras.resultado import ResultadoRegra


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


def _achado(
    codigo,
    severidade,
    titulo,
    descricao,
    *,
    regra="",
    categoria="documental",
    fato_verificado="",
    evidencia="",
    fundamentacao="",
    risco_glosa="",
    recomendacao="",
    origem_normativa="",
):
    return ResultadoRegra(
        codigo=codigo,
        severidade=severidade,
        titulo=titulo,
        descricao=descricao,
        regra=regra or codigo,
        categoria=categoria,
        resultado="achado",
        fato_verificado=fato_verificado or descricao,
        evidencia=evidencia,
        fundamentacao=fundamentacao,
        risco_glosa=risco_glosa,
        recomendacao=recomendacao,
        origem_normativa=origem_normativa,
    )


def avaliar_documento(documento, contexto=None):
    """
    Executa regras determinísticas de conferência documental.

    Não aprova, reprova, ressalva ou aplica glosa automaticamente.
    O resultado serve de subsídio à análise humana.
    """

    achados = []

    if not documento.lancamento_id:
        achados.append(
            _achado(
                "SEM_LANCAMENTO",
                "critico",
                "Documento sem lançamento vinculado",
                "O documento não está associado a um lançamento financeiro, o que impede a conferência integrada.",
                fato_verificado="Ausência de vínculo entre documento e lançamento.",
                evidencia=f"Documento #{documento.pk}.",
                risco_glosa="Potencial, caso a despesa não possa ser vinculada e comprovada.",
                recomendacao="Vincular o documento ao lançamento correspondente e conferir a despesa.",
            )
        )

    if not documento.documento_legivel:
        achados.append(
            _achado(
                "NAO_LEGIVEL",
                "alerta",
                "Legibilidade ainda não confirmada",
                "O checklist do documento não registra confirmação de que o arquivo está legível.",
                recomendacao="Conferir a legibilidade integral do documento.",
            )
        )

    if not documento.dados_compativeis:
        achados.append(
            _achado(
                "DADOS_NAO_COMPATIVEIS",
                "alerta",
                "Compatibilidade dos dados não confirmada",
                "Os dados do documento ainda não foram marcados como compatíveis com os dados cadastrados.",
                recomendacao="Comparar emitente, favorecido, valores, datas e demais dados cadastrais.",
            )
        )

    if (
        documento.tipo
        in {
            Documento.Tipo.NOTA_FISCAL,
            Documento.Tipo.FOLHA,
            Documento.Tipo.GUIA,
        }
        and not documento.pagamento_comprovado
    ):
        achados.append(
            _achado(
                "SEM_COMPROVANTE_PAGAMENTO",
                "critico",
                "Pagamento não comprovado",
                "Não há confirmação de comprovante de pagamento para este documento.",
                fato_verificado="Ausência de confirmação da comprovação do pagamento.",
                risco_glosa="Elevado se o efetivo pagamento da despesa não for demonstrado.",
                recomendacao="Apresentar e conferir comprovante de pagamento compatível com a despesa.",
            )
        )

    if documento.termo_id and not documento.vigencia_valida:
        achados.append(
            _achado(
                "VIGENCIA_NAO_CONFIRMADA",
                "alerta",
                "Vigência ainda não validada",
                "O checklist não confirma que a data do documento está dentro da vigência do Termo.",
                recomendacao="Conferir a data da despesa em relação à vigência da parceria.",
            )
        )

    if (
        documento.tipo == Documento.Tipo.NOTA_FISCAL
        and not documento.atesto_valido
    ):
        achados.append(
            _achado(
                "ATESTO_NAO_CONFIRMADO",
                "alerta",
                "Atesto não confirmado",
                "O documento fiscal ainda não possui confirmação de atesto válido.",
                recomendacao="Verificar a comprovação do recebimento do bem ou da execução do serviço.",
            )
        )

    lancamento = documento.lancamento

    if lancamento:
        if (
            documento.numero_documento
            and lancamento.numero_documento
            and documento.numero_documento.strip().lower()
            != lancamento.numero_documento.strip().lower()
        ):
            achados.append(
                _achado(
                    "NUMERO_DIVERGENTE",
                    "critico",
                    "Número do documento divergente",
                    f"Documento: {documento.numero_documento}. Lançamento: {lancamento.numero_documento}.",
                    fato_verificado="Divergência entre números de documento.",
                    evidencia=(
                        f"Documento={documento.numero_documento}; "
                        f"lançamento={lancamento.numero_documento}."
                    ),
                    recomendacao="Confirmar qual documento corresponde efetivamente ao lançamento.",
                )
            )

        if (
            documento.data_documento
            and lancamento.data_documento
            and documento.data_documento != lancamento.data_documento
        ):
            achados.append(
                _achado(
                    "DATA_DIVERGENTE",
                    "alerta",
                    "Data do documento divergente",
                    (
                        f"Documento: {documento.data_documento:%d/%m/%Y}. "
                        f"Lançamento: {lancamento.data_documento:%d/%m/%Y}."
                    ),
                    fato_verificado="Divergência entre datas do documento e do lançamento.",
                    recomendacao="Conferir a data correta antes da conclusão da análise.",
                )
            )

        if not lancamento.data_pagamento:
            achados.append(
                _achado(
                    "LANCAMENTO_SEM_DATA_PAGAMENTO",
                    "alerta",
                    "Lançamento sem data de pagamento",
                    "O lançamento vinculado não possui data de pagamento informada.",
                    recomendacao="Informar e conferir a data efetiva do pagamento.",
                )
            )

        if lancamento.tipo_glosa != lancamento.TipoGlosa.NENHUMA:
            achados.append(
                _achado(
                    "GLOSA_EXISTENTE",
                    "info",
                    "Lançamento já possui glosa",
                    (
                        f"Tipo: {lancamento.get_tipo_glosa_display()}. "
                        f"Valor: R$ {lancamento.valor_glosa}."
                    ),
                    resultado="informativo",
                )
            )

    if documento.numero_documento:
        duplicados = Documento.objects.filter(
            empresa=documento.empresa,
            numero_documento__iexact=documento.numero_documento.strip(),
        ).exclude(pk=documento.pk)

        if documento.data_documento:
            duplicados = duplicados.filter(
                data_documento=documento.data_documento
            )

        if duplicados.exists():
            achados.append(
                _achado(
                    "POSSIVEL_DUPLICIDADE",
                    "critico",
                    "Possível documento duplicado",
                    "Foi localizado outro documento da mesma OSC com o mesmo número e data.",
                    fato_verificado="Existe outro documento com mesmo número e data no mesmo escopo.",
                    evidencia=f"Quantidade adicional localizada: {duplicados.count()}.",
                    risco_glosa="Elevado se houver duplicidade de despesa ou pagamento.",
                    recomendacao="Comparar os documentos e os pagamentos antes da aprovação.",
                )
            )

    termo = documento.termo

    if termo and documento.data_documento:
        inicio = _parse_data(
            getattr(termo, "inicioVigencia", None)
        )
        fim = _parse_data(
            getattr(termo, "terminoVigencia", None)
        )

        if inicio and documento.data_documento < inicio:
            achados.append(
                _achado(
                    "ANTES_DA_VIGENCIA",
                    "critico",
                    "Documento anterior à vigência",
                    (
                        "A data do documento é anterior ao início da "
                        f"vigência ({inicio:%d/%m/%Y})."
                    ),
                    fato_verificado="Documento com data anterior ao início da vigência.",
                    evidencia=(
                        f"Documento={documento.data_documento:%d/%m/%Y}; "
                        f"início={inicio:%d/%m/%Y}."
                    ),
                    risco_glosa="Elevado, sujeito à análise do fundamento e das regras aplicáveis.",
                    recomendacao="Verificar a elegibilidade temporal da despesa.",
                )
            )

        if fim and documento.data_documento > fim:
            achados.append(
                _achado(
                    "APOS_A_VIGENCIA",
                    "critico",
                    "Documento posterior à vigência",
                    (
                        "A data do documento é posterior ao fim da "
                        f"vigência ({fim:%d/%m/%Y})."
                    ),
                    fato_verificado="Documento com data posterior ao término da vigência.",
                    evidencia=(
                        f"Documento={documento.data_documento:%d/%m/%Y}; "
                        f"término={fim:%d/%m/%Y}."
                    ),
                    risco_glosa="Elevado, sujeito à análise do fundamento e das regras aplicáveis.",
                    recomendacao="Verificar a elegibilidade temporal da despesa.",
                )
            )

    if not achados:
        achados.append(
            ResultadoRegra(
                codigo="SEM_INCONSISTENCIA_LOCAL",
                severidade="info",
                titulo="Nenhuma inconsistência local identificada",
                descricao=(
                    "As validações automáticas disponíveis não localizaram divergências. "
                    "A revisão humana continua obrigatória."
                ),
                regra="SEM_INCONSISTENCIA_LOCAL",
                categoria="documental",
                resultado="sem_achado",
                fato_verificado="Nenhuma divergência detectada pelas regras executadas.",
                recomendacao="Prosseguir com a conferência humana da prestação de contas.",
            )
        )

    return achados
