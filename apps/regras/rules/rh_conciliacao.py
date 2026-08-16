from decimal import Decimal

from apps.documentos.models import Documento
from apps.lancamentos.models import Lancamento
from apps.regras.resultado import ResultadoRegra


def _decimal(valor):
    if valor is None:
        return Decimal("0.00")

    return Decimal(str(valor)).quantize(
        Decimal("0.01")
    )


def avaliar_conciliacao_rh_lancamento(folha, contexto=None):
    achados = []

    funcionario = folha.funcionario
    empresa = getattr(funcionario, "empresa", None)
    termo = getattr(funcionario, "termo", None)
    competencia = folha.competencia

    # ---------------------------------------------------------
    # Ponte documental explícita:
    #
    # Funcionario -> Documento.pertence -> Documento.lancamento
    #
    # Enquanto não houver FK direta entre FolhaPagamento e
    # Lancamento, esta é a evidência mais forte disponível.
    # ---------------------------------------------------------
    documentos_vinculados = (
        Documento.objects
        .filter(
            pertence=funcionario,
            lancamento__isnull=False,
        )
        .select_related(
            "lancamento",
            "empresa",
            "termo",
        )
    )

    lancamento_ids = (
        documentos_vinculados
        .values_list(
            "lancamento_id",
            flat=True,
        )
        .distinct()
    )

    lancamentos = Lancamento.objects.filter(
        pk__in=lancamento_ids
    ).select_related(
        "empresa",
        "termo",
        "prestacao",
    )

    # ---------------------------------------------------------
    # Nenhuma relação documental explícita encontrada
    # ---------------------------------------------------------
    if not lancamentos.exists():
        candidatos = Lancamento.objects.none()

        if empresa:
            candidatos = Lancamento.objects.filter(
                empresa=empresa,
                tipo_documento=Lancamento.TipoDocumento.FOLHA,
                data_documento__year=competencia.year,
                data_documento__month=competencia.month,
            )

            if termo:
                candidatos = candidatos.filter(
                    termo=termo
                )

        if candidatos.exists():
            achados.append(
                ResultadoRegra(
                    codigo="RH_LANCAMENTO_CANDIDATO_NAO_VINCULADO",
                    severidade="alerta",
                    titulo="Lançamento de folha candidato não vinculado",
                    descricao=(
                        "Foi localizado lançamento de folha na mesma "
                        "OSC/Termo e competência, porém sem vínculo "
                        "documental explícito com o trabalhador."
                    ),
                    regra="RH_LANCAMENTO_CANDIDATO_NAO_VINCULADO",
                    categoria="conciliacao_rh",
                    resultado="nao_verificado",
                    fato_verificado=(
                        "Existe lançamento potencialmente relacionado "
                        "à folha, mas sem relação documental suficiente "
                        "para confirmar a correspondência."
                    ),
                    evidencia=(
                        f"funcionario={funcionario.pk}; "
                        f"competencia={competencia:%m/%Y}; "
                        f"candidatos={candidatos.count()}."
                    ),
                    risco_glosa=(
                        "Indeterminado até que seja demonstrada a "
                        "correspondência entre folha, trabalhador, "
                        "lançamento e pagamento."
                    ),
                    recomendacao=(
                        "Vincular documentalmente a folha ao lançamento "
                        "correspondente antes da conclusão da análise."
                    ),
                )
            )

        else:
            achados.append(
                ResultadoRegra(
                    codigo="RH_LANCAMENTO_NAO_LOCALIZADO",
                    severidade="alerta",
                    titulo="Lançamento correspondente à folha não localizado",
                    descricao=(
                        "Não foi localizado lançamento diretamente "
                        "relacionado ao trabalhador por meio da "
                        "documentação disponível."
                    ),
                    regra="RH_LANCAMENTO_NAO_LOCALIZADO",
                    categoria="conciliacao_rh",
                    resultado="nao_verificado",
                    fato_verificado=(
                        "Ausência de lançamento documentalmente "
                        "relacionado à folha."
                    ),
                    evidencia=(
                        f"funcionario={funcionario.pk}; "
                        f"competencia={competencia:%m/%Y}."
                    ),
                    risco_glosa=(
                        "Indeterminado. A ausência do vínculo no sistema "
                        "não comprova inexistência da despesa."
                    ),
                    recomendacao=(
                        "Localizar o lançamento da competência e estabelecer "
                        "vínculo verificável com folha, trabalhador e pagamento."
                    ),
                )
            )

        return achados

    # ---------------------------------------------------------
    # Mais de um lançamento explicitamente vinculado
    # ---------------------------------------------------------
    if lancamentos.count() > 1:
        achados.append(
            ResultadoRegra(
                codigo="RH_MULTIPLOS_LANCAMENTOS_VINCULADOS",
                severidade="alerta",
                titulo="Múltiplos lançamentos vinculados ao trabalhador",
                descricao=(
                    "Mais de um lançamento está documentalmente "
                    "relacionado ao trabalhador na análise da competência."
                ),
                regra="RH_MULTIPLOS_LANCAMENTOS_VINCULADOS",
                categoria="conciliacao_rh",
                resultado="nao_verificado",
                fato_verificado=(
                    "Existem múltiplos lançamentos relacionados "
                    "ao mesmo trabalhador."
                ),
                evidencia=(
                    f"quantidade={lancamentos.count()}; "
                    f"lancamentos={list(lancamentos.values_list('numero_lancamento', flat=True))}."
                ),
                risco_glosa=(
                    "Indeterminado até verificar se os lançamentos "
                    "representam despesas distintas ou eventual duplicidade."
                ),
                recomendacao=(
                    "Conferir a natureza de cada lançamento, competência, "
                    "documentos e comprovantes de pagamento."
                ),
            )
        )

    valor_liquido = _decimal(
        folha.valor_liquido
    )

    total_proventos = _decimal(
        folha.total_proventos
    )

    for lancamento in lancamentos:

        # -----------------------------------------------------
        # Empresa
        # -----------------------------------------------------
        if (
            empresa
            and lancamento.empresa_id != empresa.pk
        ):
            achados.append(
                ResultadoRegra(
                    codigo="RH_LANC_EMPRESA_DIVERGENTE",
                    severidade="critico",
                    titulo="Lançamento pertence a outra OSC",
                    descricao=(
                        "O lançamento documentalmente relacionado "
                        "ao trabalhador pertence a empresa/OSC diferente."
                    ),
                    regra="RH_LANC_EMPRESA_DIVERGENTE",
                    categoria="conciliacao_rh",
                    resultado="achado",
                    fato_verificado=(
                        "Empresa do trabalhador e empresa do lançamento "
                        "não coincidem."
                    ),
                    evidencia=(
                        f"empresa_funcionario={empresa.pk}; "
                        f"empresa_lancamento={lancamento.empresa_id}; "
                        f"lancamento={lancamento.numero_lancamento}."
                    ),
                    risco_glosa=(
                        "Elevado enquanto não for esclarecida a correta "
                        "imputação da despesa."
                    ),
                    recomendacao=(
                        "Conferir OSC, trabalhador, Termo e lançamento "
                        "antes da aprovação."
                    ),
                )
            )

        # -----------------------------------------------------
        # Termo
        # -----------------------------------------------------
        if (
            termo
            and lancamento.termo_id
            and lancamento.termo_id != termo.pk
        ):
            achados.append(
                ResultadoRegra(
                    codigo="RH_LANC_TERMO_DIVERGENTE",
                    severidade="critico",
                    titulo="Lançamento pertence a outro Termo",
                    descricao=(
                        "O lançamento relacionado ao trabalhador está "
                        "vinculado a Termo diferente daquele informado "
                        "para o vínculo de RH."
                    ),
                    regra="RH_LANC_TERMO_DIVERGENTE",
                    categoria="conciliacao_rh",
                    resultado="achado",
                    fato_verificado=(
                        "Divergência entre Termo do trabalhador "
                        "e Termo do lançamento."
                    ),
                    evidencia=(
                        f"termo_funcionario={termo.pk}; "
                        f"termo_lancamento={lancamento.termo_id}; "
                        f"lancamento={lancamento.numero_lancamento}."
                    ),
                    risco_glosa=(
                        "Elevado até confirmar a parceria à qual "
                        "a despesa deve ser imputada."
                    ),
                    recomendacao=(
                        "Conferir o vínculo da despesa com o Plano de Trabalho "
                        "e o Termo correto."
                    ),
                )
            )

        # -----------------------------------------------------
        # Competência
        # -----------------------------------------------------
        if (
            lancamento.data_documento.year != competencia.year
            or lancamento.data_documento.month != competencia.month
        ):
            achados.append(
                ResultadoRegra(
                    codigo="RH_LANC_COMPETENCIA_DIVERGENTE",
                    severidade="critico",
                    titulo="Competência do lançamento divergente",
                    descricao=(
                        "A data do documento do lançamento pertence "
                        "a competência diferente da folha de pagamento."
                    ),
                    regra="RH_LANC_COMPETENCIA_DIVERGENTE",
                    categoria="conciliacao_rh",
                    resultado="achado",
                    fato_verificado=(
                        "Competência da folha e data documental "
                        "do lançamento não coincidem."
                    ),
                    evidencia=(
                        f"folha={competencia:%m/%Y}; "
                        f"lancamento={lancamento.data_documento:%m/%Y}; "
                        f"numero={lancamento.numero_lancamento}."
                    ),
                    risco_glosa=(
                        "Elevado até que seja demonstrado que o lançamento "
                        "corresponde efetivamente à competência analisada."
                    ),
                    recomendacao=(
                        "Conferir competência, folha, documento e período "
                        "de apropriação da despesa."
                    ),
                )
            )

        # -----------------------------------------------------
        # Valor
        #
        # Não assumimos que o critério correto seja sempre
        # líquido ou bruto. Consideramos ambos como referências
        # possíveis e sinalizamos somente quando não coincide
        # com nenhuma delas.
        # -----------------------------------------------------
        valor_lancamento = _decimal(
            lancamento.valor_documento
        )

        if valor_lancamento not in {
            valor_liquido,
            total_proventos,
        }:
            achados.append(
                ResultadoRegra(
                    codigo="RH_LANC_VALOR_NAO_CONCILIADO",
                    severidade="alerta",
                    titulo="Valor do lançamento não conciliado com a folha",
                    descricao=(
                        "O valor do lançamento não coincide com o valor "
                        "líquido nem com o total de proventos calculados "
                        "para a folha."
                    ),
                    regra="RH_LANC_VALOR_NAO_CONCILIADO",
                    categoria="conciliacao_rh",
                    resultado="nao_verificado",
                    fato_verificado=(
                        "Não houve correspondência direta entre o valor "
                        "lançado e as principais referências da folha."
                    ),
                    evidencia=(
                        f"lancamento={valor_lancamento}; "
                        f"liquido={valor_liquido}; "
                        f"proventos={total_proventos}; "
                        f"numero={lancamento.numero_lancamento}."
                    ),
                    risco_glosa=(
                        "Indeterminado até esclarecer a composição do valor "
                        "apresentado na prestação de contas."
                    ),
                    recomendacao=(
                        "Conferir se o lançamento representa valor líquido, "
                        "bruto, rateio, agrupamento ou outra composição "
                        "prevista e documentalmente demonstrada."
                    ),
                )
            )

        # -----------------------------------------------------
        # Pagamento
        # -----------------------------------------------------
        possui_comprovante_direto = bool(
            lancamento.comprovante_pagamento
        )

        possui_comprovante_documental = (
            Documento.objects.filter(
                lancamento=lancamento,
                tipo=Documento.Tipo.COMPROVANTE,
            ).exists()
        )

        if (
            not possui_comprovante_direto
            and not possui_comprovante_documental
        ):
            achados.append(
                ResultadoRegra(
                    codigo="RH_LANC_PAGAMENTO_NAO_COMPROVADO",
                    severidade="alerta",
                    titulo="Comprovante do pagamento não localizado",
                    descricao=(
                        "O lançamento relacionado à folha não possui "
                        "comprovante direto nem documento classificado "
                        "como comprovante de pagamento."
                    ),
                    regra="RH_LANC_PAGAMENTO_NAO_COMPROVADO",
                    categoria="conciliacao_rh",
                    resultado="nao_verificado",
                    fato_verificado=(
                        "Não foi localizada evidência documental "
                        "do pagamento vinculada ao lançamento."
                    ),
                    evidencia=(
                        f"lancamento={lancamento.numero_lancamento}."
                    ),
                    risco_glosa=(
                        "Indeterminado até a comprovação do efetivo "
                        "desembolso da despesa."
                    ),
                    recomendacao=(
                        "Localizar e conferir comprovante de pagamento, "
                        "favorecido, valor e data."
                    ),
                )
            )

    # ---------------------------------------------------------
    # Possível duplicidade entre lançamentos vinculados
    # ---------------------------------------------------------
    lista_lancamentos = list(lancamentos)

    for indice, primeiro in enumerate(lista_lancamentos):
        for segundo in lista_lancamentos[indice + 1:]:

            mesma_data = (
                primeiro.data_documento
                == segundo.data_documento
            )

            mesmo_valor = (
                primeiro.valor_documento
                == segundo.valor_documento
            )

            mesmo_documento = (
                bool(primeiro.numero_documento)
                and bool(segundo.numero_documento)
                and primeiro.numero_documento.strip().lower()
                == segundo.numero_documento.strip().lower()
            )

            if (
                mesma_data
                and mesmo_valor
                and mesmo_documento
            ):
                achados.append(
                    ResultadoRegra(
                        codigo="RH_POSSIVEL_DUPLICIDADE_LANCAMENTO",
                        severidade="critico",
                        titulo="Possível duplicidade de despesa de RH",
                        descricao=(
                            "Foram localizados lançamentos relacionados "
                            "ao trabalhador com documento, data e valor "
                            "coincidentes."
                        ),
                        regra="RH_POSSIVEL_DUPLICIDADE_LANCAMENTO",
                        categoria="conciliacao_rh",
                        resultado="achado",
                        fato_verificado=(
                            "Coincidência de elementos relevantes entre "
                            "dois lançamentos."
                        ),
                        evidencia=(
                            f"lancamento_1={primeiro.numero_lancamento}; "
                            f"lancamento_2={segundo.numero_lancamento}; "
                            f"documento={primeiro.numero_documento}; "
                            f"valor={primeiro.valor_documento}; "
                            f"data={primeiro.data_documento:%d/%m/%Y}."
                        ),
                        risco_glosa=(
                            "Elevado caso seja confirmado pagamento "
                            "ou apropriação duplicada da mesma despesa."
                        ),
                        recomendacao=(
                            "Comparar os lançamentos, documentos e pagamentos "
                            "antes da conclusão da análise."
                        ),
                    )
                )

    return achados
