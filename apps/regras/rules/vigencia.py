from datetime import datetime

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


def avaliar_vigencia_lancamento(lancamento, contexto=None):
    achados = []

    termo = getattr(lancamento, "termo", None)

    if not termo:
        achados.append(
            ResultadoRegra(
                codigo="VIG_TERMO_NAO_VINCULADO",
                severidade="alerta",
                titulo="Termo não vinculado ao lançamento",
                descricao=(
                    "Não foi possível verificar a elegibilidade temporal da "
                    "despesa porque o lançamento não possui Termo vinculado."
                ),
                regra="VIG_TERMO_NAO_VINCULADO",
                categoria="vigencia",
                resultado="nao_verificado",
                fato_verificado=(
                    "Ausência de Termo vinculado ao lançamento."
                ),
                evidencia=(
                    f"Lançamento {lancamento.numero_lancamento} "
                    "sem relacionamento com Termo."
                ),
                risco_glosa=(
                    "Indeterminado até que a vigência aplicável seja identificada."
                ),
                recomendacao=(
                    "Vincular o lançamento ao Termo correspondente e "
                    "reexecutar a análise temporal."
                ),
            )
        )
        return achados

    inicio = _parse_data(
        getattr(termo, "inicioVigencia", None)
    )

    fim = _parse_data(
        getattr(termo, "terminoVigencia", None)
    )

    if not inicio or not fim:
        achados.append(
            ResultadoRegra(
                codigo="VIG_PERIODO_NAO_VERIFICAVEL",
                severidade="alerta",
                titulo="Período de vigência não verificável",
                descricao=(
                    "O Termo vinculado não possui período de vigência "
                    "completo ou em formato reconhecido pelo motor."
                ),
                regra="VIG_PERIODO_NAO_VERIFICAVEL",
                categoria="vigencia",
                resultado="nao_verificado",
                fato_verificado=(
                    "Início ou término da vigência ausente ou não interpretável."
                ),
                evidencia=(
                    f"inicioVigencia={getattr(termo, 'inicioVigencia', None)}; "
                    f"terminoVigencia={getattr(termo, 'terminoVigencia', None)}."
                ),
                risco_glosa=(
                    "Indeterminado até que a vigência seja documentalmente confirmada."
                ),
                recomendacao=(
                    "Conferir o instrumento da parceria e registrar corretamente "
                    "as datas de início e término da vigência."
                ),
            )
        )
        return achados

    datas_analisadas = []

    if getattr(lancamento, "data_documento", None):
        datas_analisadas.append(
            ("documento", lancamento.data_documento)
        )

    if getattr(lancamento, "data_pagamento", None):
        datas_analisadas.append(
            ("pagamento", lancamento.data_pagamento)
        )

    if not datas_analisadas:
        achados.append(
            ResultadoRegra(
                codigo="VIG_DATA_NAO_INFORMADA",
                severidade="alerta",
                titulo="Data necessária à análise temporal não informada",
                descricao=(
                    "O lançamento não possui data de documento ou pagamento "
                    "suficiente para a verificação temporal."
                ),
                regra="VIG_DATA_NAO_INFORMADA",
                categoria="vigencia",
                resultado="nao_verificado",
                fato_verificado=(
                    "Ausência das datas necessárias à conferência."
                ),
                evidencia=(
                    f"Lançamento {lancamento.numero_lancamento}."
                ),
                risco_glosa=(
                    "Indeterminado até que as datas sejam confirmadas."
                ),
                recomendacao=(
                    "Informar e conferir as datas documentais e financeiras "
                    "antes da conclusão da análise."
                ),
            )
        )
        return achados

    for tipo_data, data_analisada in datas_analisadas:

        if data_analisada < inicio:
            achados.append(
                ResultadoRegra(
                    codigo=f"VIG_{tipo_data.upper()}_ANTES_INICIO",
                    severidade="critico",
                    titulo=(
                        f"Data de {tipo_data} anterior ao início da vigência"
                    ),
                    descricao=(
                        f"A data de {tipo_data} do lançamento é anterior "
                        "ao início da vigência do Termo."
                    ),
                    regra="VIG_FORA_PERIODO",
                    categoria="vigencia",
                    resultado="achado",
                    fato_verificado=(
                        f"Data de {tipo_data} anterior à vigência."
                    ),
                    evidencia=(
                        f"{tipo_data}={data_analisada:%d/%m/%Y}; "
                        f"início={inicio:%d/%m/%Y}; "
                        f"fim={fim:%d/%m/%Y}."
                    ),
                    risco_glosa=(
                        "Elevado até que a elegibilidade temporal da despesa "
                        "seja demonstrada à luz das normas aplicáveis."
                    ),
                    recomendacao=(
                        "Verificar a natureza da despesa, o instrumento da parceria, "
                        "a legislação vigente e eventual justificativa antes da decisão."
                    ),
                )
            )

        elif data_analisada > fim:
            achados.append(
                ResultadoRegra(
                    codigo=f"VIG_{tipo_data.upper()}_APOS_FIM",
                    severidade="critico",
                    titulo=(
                        f"Data de {tipo_data} posterior ao término da vigência"
                    ),
                    descricao=(
                        f"A data de {tipo_data} do lançamento é posterior "
                        "ao término da vigência do Termo."
                    ),
                    regra="VIG_FORA_PERIODO",
                    categoria="vigencia",
                    resultado="achado",
                    fato_verificado=(
                        f"Data de {tipo_data} posterior à vigência."
                    ),
                    evidencia=(
                        f"{tipo_data}={data_analisada:%d/%m/%Y}; "
                        f"início={inicio:%d/%m/%Y}; "
                        f"fim={fim:%d/%m/%Y}."
                    ),
                    risco_glosa=(
                        "Elevado até que a elegibilidade temporal da despesa "
                        "seja demonstrada à luz das normas aplicáveis."
                    ),
                    recomendacao=(
                        "Verificar a natureza da despesa, o instrumento da parceria, "
                        "a legislação vigente e eventual justificativa antes da decisão."
                    ),
                )
            )

    return achados
