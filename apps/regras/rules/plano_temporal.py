from apps.regras.resultado import ResultadoRegra


def avaliar_execucao_temporal_item(resumo):
    achados = []

    if (
        resumo.inicio_previsto is None
        and resumo.fim_previsto is None
    ):
        achados.append(
            ResultadoRegra(
                codigo="PT_ITEM_SEM_PERIODO_PREVISTO",
                severidade="info",
                titulo="Item sem período estruturado",
                descricao=(
                    "O item do Plano de Trabalho não possui "
                    "início ou término previstos de execução "
                    "registrados de forma estruturada."
                ),
                regra="PT_ITEM_SEM_PERIODO_PREVISTO",
                categoria="plano_execucao_temporal",
                resultado="informativo",
                fato_verificado=(
                    "Não existem parâmetros temporais "
                    "estruturados para o item."
                ),
                evidencia="",
                risco_glosa="",
                recomendacao=(
                    "Conferir o Plano de Trabalho original "
                    "quando a análise temporal for necessária."
                ),
            )
        )

    if resumo.sem_data:
        achados.append(
            ResultadoRegra(
                codigo="PT_EXEC_DATA_NAO_IDENTIFICADA",
                severidade="alerta",
                titulo="Data da execução não identificada",
                descricao=(
                    "Há lançamento vinculado ao item sem data "
                    "suficiente para comparação com o período "
                    "previsto."
                ),
                regra="PT_EXEC_DATA_NAO_IDENTIFICADA",
                categoria="plano_execucao_temporal",
                resultado="nao_verificado",
                fato_verificado=(
                    "Não foi possível determinar a data "
                    "de referência de um ou mais lançamentos."
                ),
                evidencia=(
                    f"quantidade={len(resumo.sem_data)}."
                ),
                risco_glosa=(
                    "Indeterminado até que o período efetivo "
                    "da despesa seja comprovado."
                ),
                recomendacao=(
                    "Conferir documento fiscal, competência, "
                    "atesto, pagamento e demais evidências "
                    "temporais."
                ),
            )
        )

    if resumo.antes_periodo:
        datas = [
            item.data_referencia.isoformat()
            for item in resumo.antes_periodo
            if item.data_referencia
        ]

        achados.append(
            ResultadoRegra(
                codigo="PT_EXEC_ANTES_PERIODO_PREVISTO",
                severidade="alerta",
                titulo="Execução anterior ao período previsto",
                descricao=(
                    "Há lançamento vinculado cuja data de "
                    "referência é anterior ao início previsto "
                    "para execução do item."
                ),
                regra="PT_EXEC_ANTES_PERIODO_PREVISTO",
                categoria="plano_execucao_temporal",
                resultado="achado",
                fato_verificado=(
                    "Foi identificada execução anterior ao "
                    "período estruturado do item."
                ),
                evidencia=(
                    f"inicio_previsto="
                    f"{resumo.inicio_previsto}; "
                    f"quantidade="
                    f"{len(resumo.antes_periodo)}; "
                    f"datas={','.join(datas)}."
                ),
                risco_glosa=(
                    "Potencial, dependendo da competência real "
                    "da despesa, da versão do Plano e de eventual "
                    "alteração ou autorização aplicável."
                ),
                recomendacao=(
                    "Conferir competência, fato gerador, atesto, "
                    "Plano aplicável e eventual alteração autorizada."
                ),
            )
        )

    if resumo.depois_periodo:
        datas = [
            item.data_referencia.isoformat()
            for item in resumo.depois_periodo
            if item.data_referencia
        ]

        achados.append(
            ResultadoRegra(
                codigo="PT_EXEC_APOS_PERIODO_PREVISTO",
                severidade="alerta",
                titulo="Execução posterior ao período previsto",
                descricao=(
                    "Há lançamento vinculado cuja data de "
                    "referência é posterior ao término previsto "
                    "para execução do item."
                ),
                regra="PT_EXEC_APOS_PERIODO_PREVISTO",
                categoria="plano_execucao_temporal",
                resultado="achado",
                fato_verificado=(
                    "Foi identificada execução posterior ao "
                    "período estruturado do item."
                ),
                evidencia=(
                    f"fim_previsto="
                    f"{resumo.fim_previsto}; "
                    f"quantidade="
                    f"{len(resumo.depois_periodo)}; "
                    f"datas={','.join(datas)}."
                ),
                risco_glosa=(
                    "Potencial, dependendo da competência real "
                    "da despesa, da vigência do instrumento "
                    "e de eventual autorização válida."
                ),
                recomendacao=(
                    "Conferir competência, vigência, documento "
                    "fiscal, pagamento e alterações do Plano."
                ),
            )
        )

    if (
        resumo.quantidade_lancamentos > 0
        and not resumo.fora_periodo
        and not resumo.sem_data
        and (
            resumo.inicio_previsto is not None
            or resumo.fim_previsto is not None
        )
    ):
        achados.append(
            ResultadoRegra(
                codigo="PT_EXEC_PERIODO_COMPATIVEL",
                severidade="info",
                titulo="Execução dentro do período previsto",
                descricao=(
                    "Os lançamentos vinculados possuem datas "
                    "compatíveis com o período estruturado "
                    "do item."
                ),
                regra="PT_EXEC_PERIODO_COMPATIVEL",
                categoria="plano_execucao_temporal",
                resultado="informativo",
                fato_verificado=(
                    "Não foi detectada extrapolação temporal."
                ),
                evidencia=(
                    f"quantidade="
                    f"{resumo.quantidade_lancamentos}."
                ),
                risco_glosa="",
                recomendacao=(
                    "Manter a conferência documental e "
                    "da competência da despesa."
                ),
            )
        )

    return achados
