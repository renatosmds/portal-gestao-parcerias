from datetime import datetime
from decimal import Decimal

from apps.regras.resultado import ResultadoRegra


def _d(valor):
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01")
    )


def _parse_data(valor):
    if not valor:
        return None

    if hasattr(valor, "year"):
        return valor

    texto = str(valor).strip()

    for formato in (
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
    ):
        try:
            return datetime.strptime(
                texto,
                formato,
            ).date()
        except ValueError:
            continue

    return None


def avaliar_verbas_trabalhistas_rh(folha, contexto=None):
    achados = []

    funcionario = folha.funcionario
    termo = getattr(funcionario, "termo", None)

    admissao = getattr(
        funcionario,
        "data_admissao",
        None,
    )

    desligamento = getattr(
        funcionario,
        "data_desligamento",
        None,
    )

    aviso_previo = _d(
        getattr(funcionario, "avisoPrevio", None)
    )

    ferias = _d(
        getattr(funcionario, "avosFerias", None)
    )

    terco_ferias = _d(
        getattr(funcionario, "avosTercoFerias", None)
    )

    decimo_terceiro = _d(
        getattr(funcionario, "avos13Salario", None)
    )

    multa_fgts = _d(
        getattr(funcionario, "multafgts", None)
    )

    total_verba_rescisoria = _d(
        getattr(
            funcionario,
            "totalVerbaRescisoria",
            None,
        )
    )

    total_rescisao = _d(
        getattr(
            funcionario,
            "totalRescisao",
            None,
        )
    )

    componentes_rescisorios = (
        aviso_previo
        + ferias
        + terco_ferias
        + decimo_terceiro
        + multa_fgts
    )

    possui_verba_rescisoria = any(
        valor > 0
        for valor in (
            aviso_previo,
            ferias,
            terco_ferias,
            decimo_terceiro,
            multa_fgts,
            total_verba_rescisoria,
            total_rescisao,
        )
    )

    # ---------------------------------------------------------
    # Datas do vínculo
    # ---------------------------------------------------------
    if (
        admissao
        and desligamento
        and desligamento < admissao
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_DESLIGAMENTO_ANTES_ADMISSAO",
                severidade="critico",
                titulo="Desligamento anterior à admissão",
                descricao=(
                    "A data de desligamento registrada é anterior "
                    "à data de admissão do trabalhador."
                ),
                regra="RH_DESLIGAMENTO_ANTES_ADMISSAO",
                categoria="verbas_trabalhistas",
                resultado="achado",
                fato_verificado=(
                    "Inconsistência cronológica no vínculo trabalhista."
                ),
                evidencia=(
                    f"admissao={admissao:%d/%m/%Y}; "
                    f"desligamento={desligamento:%d/%m/%Y}."
                ),
                risco_glosa=(
                    "Elevado enquanto o período do vínculo permanecer "
                    "inconsistente."
                ),
                recomendacao=(
                    "Conferir contrato, admissão, desligamento e documentos "
                    "trabalhistas antes da análise financeira."
                ),
            )
        )

    # ---------------------------------------------------------
    # Verbas rescisórias sem desligamento
    # ---------------------------------------------------------
    if (
        possui_verba_rescisoria
        and not desligamento
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_VERBA_RESCISORIA_SEM_DESLIGAMENTO",
                severidade="alerta",
                titulo="Verba rescisória sem desligamento informado",
                descricao=(
                    "Foram identificados valores de natureza rescisória "
                    "ou proporcional, mas não existe data de desligamento "
                    "registrada."
                ),
                regra="RH_VERBA_RESCISORIA_SEM_DESLIGAMENTO",
                categoria="verbas_trabalhistas",
                resultado="nao_verificado",
                fato_verificado=(
                    "Existem valores rescisórios sem data de desligamento."
                ),
                evidencia=(
                    f"aviso_previo={aviso_previo}; "
                    f"ferias={ferias}; "
                    f"terco_ferias={terco_ferias}; "
                    f"decimo_terceiro={decimo_terceiro}; "
                    f"multa_fgts={multa_fgts}; "
                    f"total_verba_rescisoria={total_verba_rescisoria}; "
                    f"total_rescisao={total_rescisao}."
                ),
                risco_glosa=(
                    "Indeterminado até que a natureza das verbas e "
                    "a ocorrência que lhes deu origem sejam comprovadas."
                ),
                recomendacao=(
                    "Conferir desligamento, TRCT, férias, 13º, FGTS "
                    "e demais documentos pertinentes."
                ),
            )
        )

    # ---------------------------------------------------------
    # Férias sem 1/3
    # ---------------------------------------------------------
    if ferias > 0 and terco_ferias <= 0:
        achados.append(
            ResultadoRegra(
                codigo="RH_FERIAS_SEM_TERCO_IDENTIFICADO",
                severidade="alerta",
                titulo="Férias sem adicional de 1/3 identificado",
                descricao=(
                    "Existe valor de férias registrado, mas não foi "
                    "identificado valor correspondente ao adicional "
                    "de um terço no cadastro disponível."
                ),
                regra="RH_FERIAS_SEM_TERCO_IDENTIFICADO",
                categoria="verbas_trabalhistas",
                resultado="nao_verificado",
                fato_verificado=(
                    "Valor de férias existente sem valor de 1/3 identificado."
                ),
                evidencia=(
                    f"ferias={ferias}; "
                    f"terco_ferias={terco_ferias}."
                ),
                risco_glosa=(
                    "Indeterminado até a conferência da composição "
                    "e da documentação trabalhista."
                ),
                recomendacao=(
                    "Conferir recibo de férias, folha, período aquisitivo "
                    "e memória de cálculo."
                ),
            )
        )

    # ---------------------------------------------------------
    # 1/3 sem férias
    # ---------------------------------------------------------
    if terco_ferias > 0 and ferias <= 0:
        achados.append(
            ResultadoRegra(
                codigo="RH_TERCO_SEM_FERIAS_IDENTIFICADAS",
                severidade="alerta",
                titulo="Adicional de 1/3 sem férias identificadas",
                descricao=(
                    "Existe valor de adicional de férias registrado, "
                    "mas não foi identificado valor correspondente "
                    "às férias no cadastro disponível."
                ),
                regra="RH_TERCO_SEM_FERIAS_IDENTIFICADAS",
                categoria="verbas_trabalhistas",
                resultado="nao_verificado",
                fato_verificado=(
                    "Valor de 1/3 existente sem férias identificadas."
                ),
                evidencia=(
                    f"ferias={ferias}; "
                    f"terco_ferias={terco_ferias}."
                ),
                risco_glosa=(
                    "Indeterminado até a conferência da composição."
                ),
                recomendacao=(
                    "Conferir folha, recibo de férias e memória de cálculo."
                ),
            )
        )

    # ---------------------------------------------------------
    # Relação temporal com o Termo
    # ---------------------------------------------------------
    if termo:
        inicio_termo = _parse_data(
            getattr(termo, "inicioVigencia", None)
        )

        fim_termo = _parse_data(
            getattr(termo, "terminoVigencia", None)
        )

        if (
            possui_verba_rescisoria
            and inicio_termo
            and fim_termo
            and admissao
            and desligamento
        ):
            sem_sobreposicao = (
                desligamento < inicio_termo
                or admissao > fim_termo
            )

            if sem_sobreposicao:
                achados.append(
                    ResultadoRegra(
                        codigo="RH_RESCISAO_SEM_SOBREPOSICAO_TERMO",
                        severidade="critico",
                        titulo="Vínculo trabalhista sem sobreposição com a parceria",
                        descricao=(
                            "Foram identificadas verbas trabalhistas, "
                            "mas o período informado do vínculo não se "
                            "sobrepõe à vigência do Termo."
                        ),
                        regra="RH_RESCISAO_SEM_SOBREPOSICAO_TERMO",
                        categoria="verbas_trabalhistas",
                        resultado="achado",
                        fato_verificado=(
                            "Não existe sobreposição temporal entre "
                            "vínculo trabalhista e vigência da parceria."
                        ),
                        evidencia=(
                            f"admissao={admissao:%d/%m/%Y}; "
                            f"desligamento={desligamento:%d/%m/%Y}; "
                            f"inicio_termo={inicio_termo:%d/%m/%Y}; "
                            f"fim_termo={fim_termo:%d/%m/%Y}."
                        ),
                        risco_glosa=(
                            "Elevado caso a verba tenha sido integralmente "
                            "imputada à parceria sem demonstração de vínculo "
                            "temporal ou critério válido de rateio."
                        ),
                        recomendacao=(
                            "Conferir período trabalhado, origem da obrigação, "
                            "Plano de Trabalho, rateio e normas aplicáveis."
                        ),
                    )
                )

            elif (
                admissao < inicio_termo
                or desligamento > fim_termo
            ):
                achados.append(
                    ResultadoRegra(
                        codigo="RH_RESCISAO_PERIODO_PARCIAL_TERMO",
                        severidade="alerta",
                        titulo="Vínculo ultrapassa a vigência da parceria",
                        descricao=(
                            "O vínculo trabalhista possui apenas sobreposição "
                            "parcial com a vigência do Termo."
                        ),
                        regra="RH_RESCISAO_PERIODO_PARCIAL_TERMO",
                        categoria="verbas_trabalhistas",
                        resultado="nao_verificado",
                        fato_verificado=(
                            "Apenas parte do período do vínculo coincide "
                            "com a vigência da parceria."
                        ),
                        evidencia=(
                            f"admissao={admissao:%d/%m/%Y}; "
                            f"desligamento={desligamento:%d/%m/%Y}; "
                            f"inicio_termo={inicio_termo:%d/%m/%Y}; "
                            f"fim_termo={fim_termo:%d/%m/%Y}."
                        ),
                        risco_glosa=(
                            "Indeterminado até identificar qual parcela "
                            "das verbas é atribuível ao período da parceria."
                        ),
                        recomendacao=(
                            "Apurar o período efetivamente relacionado "
                            "à parceria e conferir eventual rateio."
                        ),
                    )
                )

    # ---------------------------------------------------------
    # Ambiguidade entre total e componentes
    #
    # O modelo legado possui campos de componentes e campos de
    # totalização. Não somamos automaticamente todos eles porque
    # totalVerbaRescisoria pode já conter os componentes.
    # ---------------------------------------------------------
    if (
        total_verba_rescisoria > 0
        and componentes_rescisorios > 0
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_RESCISAO_TOTAL_E_COMPONENTES_PRESENTES",
                severidade="info",
                titulo="Total rescisório e componentes registrados",
                descricao=(
                    "O cadastro possui simultaneamente componentes "
                    "rescisórios e um campo de totalização."
                ),
                regra="RH_RESCISAO_TOTAL_E_COMPONENTES_PRESENTES",
                categoria="verbas_trabalhistas",
                resultado="informativo",
                fato_verificado=(
                    "Existem valores detalhados e totalizadores "
                    "no modelo de RH."
                ),
                evidencia=(
                    f"componentes={componentes_rescisorios}; "
                    f"total_verba_rescisoria={total_verba_rescisoria}."
                ),
                risco_glosa="",
                recomendacao=(
                    "Evitar somar automaticamente total e componentes "
                    "até confirmar a composição do TRCT, prevenindo "
                    "dupla contagem."
                ),
            )
        )

    return achados
