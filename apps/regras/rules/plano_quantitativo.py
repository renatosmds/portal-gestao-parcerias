from decimal import Decimal

from apps.regras.resultado import ResultadoRegra


def avaliar_execucao_quantitativa_item(resumo):
    achados = []

    possui_parametro = (
        resumo.quantidade_prevista is not None
        or resumo.valor_unitario_previsto is not None
    )

    if not possui_parametro:
        achados.append(
            ResultadoRegra(
                codigo="PT_ITEM_SEM_PARAMETRO_QUANTITATIVO",
                severidade="info",
                titulo="Item sem parâmetros quantitativos",
                descricao=(
                    "O item não possui quantidade ou valor "
                    "unitário previstos de forma estruturada."
                ),
                regra="PT_ITEM_SEM_PARAMETRO_QUANTITATIVO",
                categoria="plano_execucao_quantitativa",
                resultado="informativo",
                fato_verificado=(
                    "Não existem parâmetros suficientes para "
                    "comparação quantitativa automática."
                ),
                evidencia="",
                risco_glosa="",
                recomendacao=(
                    "Utilizar a análise financeira global e "
                    "conferir o Plano de Trabalho original."
                ),
            )
        )

        return achados

    if (
        resumo.quantidade_prevista is not None
        and resumo.vinculos_sem_quantidade > 0
    ):
        achados.append(
            ResultadoRegra(
                codigo="PT_EXEC_QUANTIDADE_NAO_INFORMADA",
                severidade="alerta",
                titulo="Quantidade executada não informada",
                descricao=(
                    "Há lançamento vinculado ao item, mas sem "
                    "quantidade executada estruturada."
                ),
                regra="PT_EXEC_QUANTIDADE_NAO_INFORMADA",
                categoria="plano_execucao_quantitativa",
                resultado="nao_verificado",
                fato_verificado=(
                    "Existem vínculos sem quantidade executada."
                ),
                evidencia=(
                    f"vinculos_sem_quantidade="
                    f"{resumo.vinculos_sem_quantidade}."
                ),
                risco_glosa=(
                    "Indeterminado enquanto a quantidade executada "
                    "não puder ser conciliada."
                ),
                recomendacao=(
                    "Conferir nota fiscal, recibo, medição ou outro "
                    "documento de execução."
                ),
            )
        )

    if (
        resumo.valor_unitario_previsto is not None
        and resumo.vinculos_sem_valor_unitario > 0
    ):
        achados.append(
            ResultadoRegra(
                codigo="PT_EXEC_VALOR_UNITARIO_NAO_INFORMADO",
                severidade="alerta",
                titulo="Valor unitário executado não informado",
                descricao=(
                    "Há lançamento vinculado sem valor unitário "
                    "executado estruturado."
                ),
                regra="PT_EXEC_VALOR_UNITARIO_NAO_INFORMADO",
                categoria="plano_execucao_quantitativa",
                resultado="nao_verificado",
                fato_verificado=(
                    "Existem vínculos sem valor unitário executado."
                ),
                evidencia=(
                    f"vinculos_sem_valor_unitario="
                    f"{resumo.vinculos_sem_valor_unitario}."
                ),
                risco_glosa=(
                    "Indeterminado até a conciliação do preço "
                    "unitário efetivamente praticado."
                ),
                recomendacao=(
                    "Conferir documento fiscal e memória de cálculo."
                ),
            )
        )

    if resumo.quantidade_excedida:
        excesso = (
            resumo.quantidade_executada
            - resumo.quantidade_prevista
        ).quantize(
            Decimal("0.0000")
        )

        achados.append(
            ResultadoRegra(
                codigo="PT_EXEC_QUANTIDADE_SUPERIOR_PREVISTA",
                severidade="critico",
                titulo="Quantidade executada superior à prevista",
                descricao=(
                    "A quantidade acumulada dos lançamentos "
                    "vinculados supera a quantidade prevista "
                    "para o item."
                ),
                regra="PT_EXEC_QUANTIDADE_SUPERIOR_PREVISTA",
                categoria="plano_execucao_quantitativa",
                resultado="achado",
                fato_verificado=(
                    "Quantidade executada superior ao parâmetro "
                    "do Plano de Trabalho."
                ),
                evidencia=(
                    f"prevista={resumo.quantidade_prevista}; "
                    f"executada={resumo.quantidade_executada}; "
                    f"excesso={excesso}."
                ),
                risco_glosa=(
                    "Elevado enquanto não houver alteração, "
                    "remanejamento ou justificativa válida."
                ),
                recomendacao=(
                    "Conferir versão aplicável do Plano, aditivos, "
                    "remanejamentos e documentos da execução."
                ),
            )
        )

    if resumo.valor_unitario_excedido:
        diferenca = (
            resumo.maior_valor_unitario_executado
            - resumo.valor_unitario_previsto
        ).quantize(
            Decimal("0.01")
        )

        achados.append(
            ResultadoRegra(
                codigo="PT_EXEC_VALOR_UNITARIO_SUPERIOR_PREVISTO",
                severidade="alerta",
                titulo="Valor unitário superior ao previsto",
                descricao=(
                    "Foi identificado preço unitário executado "
                    "superior ao parâmetro previsto no Plano."
                ),
                regra="PT_EXEC_VALOR_UNITARIO_SUPERIOR_PREVISTO",
                categoria="plano_execucao_quantitativa",
                resultado="achado",
                fato_verificado=(
                    "Preço unitário executado superior ao previsto."
                ),
                evidencia=(
                    f"previsto={resumo.valor_unitario_previsto}; "
                    f"maior_executado="
                    f"{resumo.maior_valor_unitario_executado}; "
                    f"diferenca={diferenca}."
                ),
                risco_glosa=(
                    "Depende das regras do instrumento, da "
                    "compatibilidade com o mercado e da existência "
                    "de alteração autorizada."
                ),
                recomendacao=(
                    "Conferir Plano, pesquisa de mercado, documento "
                    "fiscal e eventual alteração autorizada."
                ),
            )
        )

    if resumo.divergencias_valor_documento > 0:
        achados.append(
            ResultadoRegra(
                codigo="PT_EXEC_TOTAL_CALCULADO_DIVERGE_DOCUMENTO",
                severidade="alerta",
                titulo="Total quantitativo diverge do documento",
                descricao=(
                    "Em pelo menos um vínculo, quantidade multiplicada "
                    "pelo valor unitário não corresponde ao valor total "
                    "do lançamento."
                ),
                regra="PT_EXEC_TOTAL_CALCULADO_DIVERGE_DOCUMENTO",
                categoria="plano_execucao_quantitativa",
                resultado="nao_verificado",
                fato_verificado=(
                    "Há divergência entre cálculo quantitativo e "
                    "valor total do lançamento."
                ),
                evidencia=(
                    f"divergencias="
                    f"{resumo.divergencias_valor_documento}."
                ),
                risco_glosa=(
                    "Indeterminado. A diferença pode decorrer de "
                    "desconto, frete, tributo, mais de um item ou "
                    "outro componente do documento."
                ),
                recomendacao=(
                    "Conferir a composição do documento antes de "
                    "qualquer conclusão financeira."
                ),
            )
        )

    return achados
