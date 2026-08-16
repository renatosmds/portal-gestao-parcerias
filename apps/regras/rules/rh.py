from calendar import monthrange

from apps.regras.resultado import ResultadoRegra


def _fim_competencia(competencia):
    ultimo_dia = monthrange(
        competencia.year,
        competencia.month,
    )[1]

    return competencia.replace(
        day=ultimo_dia
    )


def avaliar_folha_pagamento(folha, contexto=None):
    achados = []

    funcionario = folha.funcionario
    termo = getattr(funcionario, "termo", None)
    empresa = getattr(funcionario, "empresa", None)

    # ---------------------------------------------------------
    # Empresa / escopo institucional
    # ---------------------------------------------------------
    if not empresa:
        achados.append(
            ResultadoRegra(
                codigo="RH_FUNC_SEM_EMPRESA",
                severidade="critico",
                titulo="Trabalhador sem empresa/OSC vinculada",
                descricao=(
                    "O trabalhador utilizado na folha de pagamento "
                    "não possui empresa/OSC vinculada."
                ),
                regra="RH_FUNC_SEM_EMPRESA",
                categoria="recursos_humanos",
                resultado="achado",
                fato_verificado=(
                    "Ausência de empresa vinculada ao trabalhador."
                ),
                evidencia=(
                    f"Funcionário ID={funcionario.pk}."
                ),
                risco_glosa=(
                    "Elevado até que seja demonstrado a qual entidade "
                    "e parceria pertence a despesa de pessoal."
                ),
                recomendacao=(
                    "Identificar a OSC responsável pelo trabalhador "
                    "antes da conclusão da análise."
                ),
            )
        )

    # ---------------------------------------------------------
    # Termo / parceria
    # ---------------------------------------------------------
    if not termo:
        achados.append(
            ResultadoRegra(
                codigo="RH_FUNC_SEM_TERMO",
                severidade="alerta",
                titulo="Trabalhador sem Termo vinculado",
                descricao=(
                    "Não foi localizado Termo/parceria vinculado "
                    "ao trabalhador."
                ),
                regra="RH_FUNC_SEM_TERMO",
                categoria="recursos_humanos",
                resultado="nao_verificado",
                fato_verificado=(
                    "Ausência de Termo vinculado ao trabalhador."
                ),
                evidencia=(
                    f"Funcionário ID={funcionario.pk}."
                ),
                risco_glosa=(
                    "Indeterminado até que seja demonstrada a relação "
                    "do trabalhador com a parceria."
                ),
                recomendacao=(
                    "Vincular ou identificar o Termo/parceria antes "
                    "da conclusão da análise de RH."
                ),
            )
        )

    # ---------------------------------------------------------
    # Empresa do trabalhador x empresa do Termo
    # ---------------------------------------------------------
    if (
        empresa
        and termo
        and getattr(termo, "empresa_id", None)
        and termo.empresa_id != empresa.pk
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_EMPRESA_TERMO_DIVERGENTE",
                severidade="critico",
                titulo="Empresa do trabalhador divergente do Termo",
                descricao=(
                    "O trabalhador e o Termo estão vinculados "
                    "a empresas diferentes."
                ),
                regra="RH_EMPRESA_TERMO_DIVERGENTE",
                categoria="recursos_humanos",
                resultado="achado",
                fato_verificado=(
                    "Divergência entre o vínculo institucional "
                    "do trabalhador e o Termo."
                ),
                evidencia=(
                    f"empresa_funcionario={empresa.pk}; "
                    f"empresa_termo={termo.empresa_id}."
                ),
                risco_glosa=(
                    "Elevado caso a despesa de pessoal esteja sendo "
                    "imputada a parceria diversa daquela à qual "
                    "o trabalhador efetivamente pertence."
                ),
                recomendacao=(
                    "Conferir OSC, vínculo do trabalhador e Termo "
                    "antes da aprovação da despesa."
                ),
            )
        )

    # ---------------------------------------------------------
    # Competência
    # ---------------------------------------------------------
    competencia = folha.competencia

    if competencia.day != 1:
        achados.append(
            ResultadoRegra(
                codigo="RH_COMPETENCIA_FORA_PADRAO",
                severidade="alerta",
                titulo="Competência fora do padrão mensal",
                descricao=(
                    "A competência da folha não está registrada "
                    "no primeiro dia do mês."
                ),
                regra="RH_COMPETENCIA_FORA_PADRAO",
                categoria="recursos_humanos",
                resultado="achado",
                fato_verificado=(
                    "Competência cadastrada com dia diferente de 1."
                ),
                evidencia=(
                    f"competencia={competencia:%d/%m/%Y}."
                ),
                risco_glosa=(
                    "Baixo isoladamente, mas pode causar associação "
                    "incorreta entre folha, ponto e lançamento."
                ),
                recomendacao=(
                    "Padronizar a competência no primeiro dia do mês."
                ),
            )
        )

    # ---------------------------------------------------------
    # Período do vínculo trabalhista
    # ---------------------------------------------------------
    inicio_mes = competencia.replace(day=1)
    fim_mes = _fim_competencia(competencia)

    if (
        funcionario.data_admissao
        and funcionario.data_admissao > fim_mes
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_COMPETENCIA_ANTES_ADMISSAO",
                severidade="critico",
                titulo="Folha anterior à admissão",
                descricao=(
                    "A competência da folha é anterior ao início "
                    "do vínculo informado."
                ),
                regra="RH_COMPETENCIA_ANTES_ADMISSAO",
                categoria="recursos_humanos",
                resultado="achado",
                fato_verificado=(
                    "Competência integralmente anterior à admissão."
                ),
                evidencia=(
                    f"competencia={competencia:%m/%Y}; "
                    f"admissao={funcionario.data_admissao:%d/%m/%Y}."
                ),
                risco_glosa=(
                    "Elevado caso não exista vínculo ou obrigação "
                    "trabalhista correspondente ao período."
                ),
                recomendacao=(
                    "Conferir admissão, contrato, folha e documentos "
                    "da competência."
                ),
            )
        )

    if (
        funcionario.data_desligamento
        and funcionario.data_desligamento < inicio_mes
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_COMPETENCIA_APOS_DESLIGAMENTO",
                severidade="critico",
                titulo="Folha posterior ao desligamento",
                descricao=(
                    "A competência da folha é posterior ao "
                    "desligamento informado."
                ),
                regra="RH_COMPETENCIA_APOS_DESLIGAMENTO",
                categoria="recursos_humanos",
                resultado="achado",
                fato_verificado=(
                    "Competência integralmente posterior ao desligamento."
                ),
                evidencia=(
                    f"competencia={competencia:%m/%Y}; "
                    f"desligamento={funcionario.data_desligamento:%d/%m/%Y}."
                ),
                risco_glosa=(
                    "Elevado caso não se trate de verba rescisória "
                    "ou outra obrigação devidamente comprovada."
                ),
                recomendacao=(
                    "Conferir desligamento, TRCT, verbas rescisórias "
                    "e natureza do lançamento antes da decisão."
                ),
            )
        )

    # ---------------------------------------------------------
    # Folha de ponto
    # ---------------------------------------------------------
    ponto = folha.folha_ponto

    if not ponto:
        achados.append(
            ResultadoRegra(
                codigo="RH_PONTO_AUSENTE",
                severidade="alerta",
                titulo="Folha de ponto não vinculada",
                descricao=(
                    "A folha de pagamento não possui folha de ponto "
                    "vinculada."
                ),
                regra="RH_PONTO_AUSENTE",
                categoria="recursos_humanos",
                resultado="nao_verificado",
                fato_verificado=(
                    "Ausência de folha de ponto vinculada."
                ),
                evidencia=(
                    f"Folha de pagamento ID={folha.pk}; "
                    f"competência={competencia:%m/%Y}."
                ),
                risco_glosa=(
                    "Indeterminado até que frequência, faltas, atrasos "
                    "e jornada possam ser conferidos."
                ),
                recomendacao=(
                    "Vincular e conferir a folha de ponto da competência."
                ),
            )
        )

    else:
        if ponto.funcionario_id != funcionario.pk:
            achados.append(
                ResultadoRegra(
                    codigo="RH_PONTO_FUNCIONARIO_DIVERGENTE",
                    severidade="critico",
                    titulo="Folha de ponto pertence a outro trabalhador",
                    descricao=(
                        "A folha de ponto vinculada não pertence ao "
                        "mesmo trabalhador da folha de pagamento."
                    ),
                    regra="RH_PONTO_FUNCIONARIO_DIVERGENTE",
                    categoria="recursos_humanos",
                    resultado="achado",
                    fato_verificado=(
                        "Funcionários divergentes entre folha "
                        "de pagamento e folha de ponto."
                    ),
                    evidencia=(
                        f"funcionario_folha={funcionario.pk}; "
                        f"funcionario_ponto={ponto.funcionario_id}."
                    ),
                    risco_glosa=(
                        "Elevado por ausência de correspondência entre "
                        "pagamento e controle de frequência."
                    ),
                    recomendacao=(
                        "Corrigir o vínculo e conferir os documentos "
                        "do trabalhador correto."
                    ),
                )
            )

        if (
            ponto.competencia.year != competencia.year
            or ponto.competencia.month != competencia.month
        ):
            achados.append(
                ResultadoRegra(
                    codigo="RH_COMPETENCIA_PONTO_DIVERGENTE",
                    severidade="critico",
                    titulo="Competência da folha divergente do ponto",
                    descricao=(
                        "A folha de pagamento e a folha de ponto "
                        "referem-se a competências diferentes."
                    ),
                    regra="RH_COMPETENCIA_PONTO_DIVERGENTE",
                    categoria="recursos_humanos",
                    resultado="achado",
                    fato_verificado=(
                        "Competências mensais divergentes."
                    ),
                    evidencia=(
                        f"folha={competencia:%m/%Y}; "
                        f"ponto={ponto.competencia:%m/%Y}."
                    ),
                    risco_glosa=(
                        "Elevado até que seja demonstrada a correta "
                        "correspondência entre frequência e pagamento."
                    ),
                    recomendacao=(
                        "Conferir e vincular a folha de ponto da mesma "
                        "competência da folha de pagamento."
                    ),
                )
            )


    # ---------------------------------------------------------
    # Salário-base cadastrado x folha
    # ---------------------------------------------------------
    salario_cadastrado = getattr(
        funcionario,
        "salarioBase",
        None,
    )

    if (
        salario_cadastrado is not None
        and folha.salario_base != salario_cadastrado
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_SALARIO_BASE_DIVERGENTE",
                severidade="critico",
                titulo="Salário-base divergente",
                descricao=(
                    "O salário-base utilizado na folha de pagamento "
                    "difere do salário-base cadastrado para o trabalhador."
                ),
                regra="RH_SALARIO_BASE_DIVERGENTE",
                categoria="recursos_humanos",
                resultado="achado",
                fato_verificado=(
                    "Divergência entre salário cadastrado "
                    "e salário utilizado na folha."
                ),
                evidencia=(
                    f"salario_cadastrado={salario_cadastrado}; "
                    f"salario_folha={folha.salario_base}."
                ),
                risco_glosa=(
                    "Elevado até que a diferença seja justificada "
                    "por reajuste, alteração contratual, convenção "
                    "coletiva ou outro documento válido."
                ),
                recomendacao=(
                    "Conferir contrato de trabalho, alteração salarial, "
                    "convenção coletiva e Plano de Trabalho."
                ),
            )
        )

    # ---------------------------------------------------------
    # Faltas e atrasos
    # ---------------------------------------------------------
    if ponto:
        horas_faltas = ponto.horas_faltas_atrasos or 0

        if horas_faltas > 0:
            desconto_calculado = folha.desconto_faltas_atrasos

            if desconto_calculado <= 0:
                achados.append(
                    ResultadoRegra(
                        codigo="RH_FALTA_SEM_DESCONTO",
                        severidade="critico",
                        titulo="Falta ou atraso sem desconto calculado",
                        descricao=(
                            "A folha de ponto registra faltas ou atrasos, "
                            "mas não foi identificado desconto correspondente."
                        ),
                        regra="RH_FALTA_SEM_DESCONTO",
                        categoria="recursos_humanos",
                        resultado="achado",
                        fato_verificado=(
                            "Existem horas de faltas/atrasos sem reflexo "
                            "financeiro calculado."
                        ),
                        evidencia=(
                            f"horas_faltas_atrasos={horas_faltas}; "
                            f"desconto_calculado={desconto_calculado}."
                        ),
                        risco_glosa=(
                            "Elevado se a despesa apresentada à parceria "
                            "incluiu remuneração correspondente a período "
                            "não trabalhado e não justificado."
                        ),
                        recomendacao=(
                            "Conferir folha de ponto, justificativas, "
                            "abonos e folha de pagamento antes da decisão."
                        ),
                    )
                )
            else:
                achados.append(
                    ResultadoRegra(
                        codigo="RH_FALTA_COM_DESCONTO",
                        severidade="info",
                        titulo="Falta ou atraso com desconto identificado",
                        descricao=(
                            "A folha de ponto registra faltas ou atrasos "
                            "e o sistema calculou desconto correspondente."
                        ),
                        regra="RH_FALTA_COM_DESCONTO",
                        categoria="recursos_humanos",
                        resultado="informativo",
                        fato_verificado=(
                            "Existem faltas/atrasos com reflexo financeiro."
                        ),
                        evidencia=(
                            f"horas_faltas_atrasos={horas_faltas}; "
                            f"desconto_calculado={desconto_calculado}."
                        ),
                        risco_glosa="",
                        recomendacao=(
                            "Conferir se as faltas, justificativas e "
                            "descontos coincidem com os documentos da competência."
                        ),
                    )
                )

    # ---------------------------------------------------------
    # Coerência básica de horas
    # ---------------------------------------------------------
    if ponto:
        horas_previstas = ponto.horas_previstas or 0
        horas_trabalhadas = ponto.horas_trabalhadas or 0
        horas_extras = ponto.horas_extras or 0
        horas_faltas = ponto.horas_faltas_atrasos or 0

        total_registrado = (
            horas_trabalhadas
            + horas_extras
            + horas_faltas
        )

        if (
            horas_previstas > 0
            and total_registrado < horas_previstas
        ):
            diferenca = horas_previstas - total_registrado

            achados.append(
                ResultadoRegra(
                    codigo="RH_HORAS_NAO_CONCILIADAS",
                    severidade="alerta",
                    titulo="Horas da competência não conciliadas",
                    descricao=(
                        "A soma das horas trabalhadas, extras e faltas/atrasos "
                        "é inferior às horas previstas para a competência."
                    ),
                    regra="RH_HORAS_NAO_CONCILIADAS",
                    categoria="recursos_humanos",
                    resultado="nao_verificado",
                    fato_verificado=(
                        "Existe diferença entre horas previstas "
                        "e horas registradas."
                    ),
                    evidencia=(
                        f"previstas={horas_previstas}; "
                        f"trabalhadas={horas_trabalhadas}; "
                        f"extras={horas_extras}; "
                        f"faltas={horas_faltas}; "
                        f"diferenca={diferenca}."
                    ),
                    risco_glosa=(
                        "Indeterminado até a conciliação da frequência "
                        "e eventual identificação de abonos, afastamentos "
                        "ou outras ocorrências."
                    ),
                    recomendacao=(
                        "Conferir folha de ponto, justificativas, "
                        "afastamentos e registros de frequência."
                    ),
                )
            )

    # ---------------------------------------------------------
    # Encargos sociais
    # ---------------------------------------------------------
    inss_folha = folha.inss or 0

    if inss_folha < 0:
        achados.append(
            ResultadoRegra(
                codigo="RH_INSS_NEGATIVO",
                severidade="critico",
                titulo="Valor de INSS inválido",
                descricao=(
                    "O valor de INSS registrado na folha de pagamento "
                    "é negativo."
                ),
                regra="RH_INSS_NEGATIVO",
                categoria="recursos_humanos",
                resultado="achado",
                fato_verificado=(
                    "Valor negativo registrado no campo INSS."
                ),
                evidencia=(
                    f"inss={inss_folha}."
                ),
                risco_glosa=(
                    "Elevado até que o valor do encargo seja corrigido "
                    "e documentalmente demonstrado."
                ),
                recomendacao=(
                    "Conferir folha de pagamento, memória de cálculo, "
                    "guia de recolhimento e comprovante de pagamento."
                ),
            )
        )

    inss_funcionario = getattr(
        funcionario,
        "inss",
        None,
    )

    if (
        inss_funcionario is not None
        and inss_funcionario > 0
        and inss_folha > 0
        and inss_funcionario != inss_folha
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_INSS_DIVERGENTE",
                severidade="alerta",
                titulo="Valor de INSS divergente",
                descricao=(
                    "O valor de INSS registrado na folha difere do "
                    "valor de INSS cadastrado para o trabalhador."
                ),
                regra="RH_INSS_DIVERGENTE",
                categoria="recursos_humanos",
                resultado="nao_verificado",
                fato_verificado=(
                    "Valores de INSS divergentes entre os registros."
                ),
                evidencia=(
                    f"inss_funcionario={inss_funcionario}; "
                    f"inss_folha={inss_folha}."
                ),
                risco_glosa=(
                    "Indeterminado até que seja identificada a origem "
                    "da divergência e o valor efetivamente devido e pago."
                ),
                recomendacao=(
                    "Conferir memória de cálculo, folha de pagamento, "
                    "guia e comprovante de recolhimento."
                ),
            )
        )

    fgts_funcionario = getattr(
        funcionario,
        "fgts",
        None,
    )

    if (
        funcionario.tipo_vinculo == "clt"
        and fgts_funcionario is None
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_FGTS_NAO_INFORMADO",
                severidade="alerta",
                titulo="FGTS não informado",
                descricao=(
                    "O trabalhador está cadastrado como empregado CLT, "
                    "mas não possui valor de FGTS informado no cadastro."
                ),
                regra="RH_FGTS_NAO_INFORMADO",
                categoria="recursos_humanos",
                resultado="nao_verificado",
                fato_verificado=(
                    "Campo de FGTS sem valor para vínculo CLT."
                ),
                evidencia=(
                    f"funcionario={funcionario.pk}; "
                    f"tipo_vinculo={funcionario.tipo_vinculo}."
                ),
                risco_glosa=(
                    "Indeterminado até que os encargos incidentes sobre "
                    "a remuneração sejam conferidos."
                ),
                recomendacao=(
                    "Conferir folha, base de cálculo, guia do FGTS "
                    "e comprovante de recolhimento."
                ),
            )
        )

    if (
        fgts_funcionario is not None
        and fgts_funcionario < 0
    ):
        achados.append(
            ResultadoRegra(
                codigo="RH_FGTS_NEGATIVO",
                severidade="critico",
                titulo="Valor de FGTS inválido",
                descricao=(
                    "O valor de FGTS cadastrado para o trabalhador "
                    "é negativo."
                ),
                regra="RH_FGTS_NEGATIVO",
                categoria="recursos_humanos",
                resultado="achado",
                fato_verificado=(
                    "Valor negativo registrado para FGTS."
                ),
                evidencia=(
                    f"fgts={fgts_funcionario}."
                ),
                risco_glosa=(
                    "Elevado até que o encargo seja corrigido e "
                    "documentalmente comprovado."
                ),
                recomendacao=(
                    "Conferir folha, memória de cálculo, guia e "
                    "comprovante de pagamento."
                ),
            )
        )
    return achados


