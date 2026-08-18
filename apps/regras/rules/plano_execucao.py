from decimal import Decimal

from apps.regras.resultado import ResultadoRegra


def avaliar_execucao_financeira_item(
    resumo,
):
    achados = []

    if resumo.valor_previsto <= Decimal("0.00"):
        achados.append(
            ResultadoRegra(
                codigo="PT_ITEM_SEM_VALOR_PREVISTO",
                severidade="alerta",
                titulo="Item sem valor previsto",
                descricao=(
                    "O item do Plano de Trabalho não possui "
                    "valor financeiro previsto positivo."
                ),
                regra="PT_ITEM_SEM_VALOR_PREVISTO",
                categoria="plano_execucao",
                resultado="nao_verificado",
                fato_verificado=(
                    "Valor previsto igual ou inferior a zero."
                ),
                evidencia=(
                    f"valor_previsto={resumo.valor_previsto}."
                ),
                risco_glosa=(
                    "Indeterminado até confirmação da previsão "
                    "financeira aplicável."
                ),
                recomendacao=(
                    "Conferir Plano de Trabalho, versão aplicável "
                    "e eventual remanejamento."
                ),
            )
        )

        return achados

    if resumo.valor_executado > resumo.valor_previsto:
        excesso = (
            resumo.valor_executado
            - resumo.valor_previsto
        ).quantize(
            Decimal("0.01")
        )

        achados.append(
            ResultadoRegra(
                codigo="PT_ITEM_VALOR_EXCEDIDO",
                severidade="critico",
                titulo="Execução superior ao valor previsto",
                descricao=(
                    "O total dos lançamentos atualmente vinculados "
                    "ao item supera o valor previsto na versão "
                    "aplicável do Plano de Trabalho."
                ),
                regra="PT_ITEM_VALOR_EXCEDIDO",
                categoria="plano_execucao",
                resultado="achado",
                fato_verificado=(
                    "Execução financeira superior ao valor previsto."
                ),
                evidencia=(
                    f"previsto={resumo.valor_previsto}; "
                    f"executado={resumo.valor_executado}; "
                    f"excesso={excesso}."
                ),
                risco_glosa=(
                    "Elevado enquanto não houver comprovação de "
                    "alteração, remanejamento ou outra autorização "
                    "válida que suporte o valor executado."
                ),
                recomendacao=(
                    "Conferir versão do Plano, aditivos, "
                    "remanejamentos e autorizações aplicáveis."
                ),
            )
        )

    elif resumo.valor_executado == resumo.valor_previsto:
        achados.append(
            ResultadoRegra(
                codigo="PT_ITEM_TOTALMENTE_EXECUTADO",
                severidade="info",
                titulo="Item totalmente executado",
                descricao=(
                    "O valor executado corresponde integralmente "
                    "ao valor previsto para o item."
                ),
                regra="PT_ITEM_TOTALMENTE_EXECUTADO",
                categoria="plano_execucao",
                resultado="informativo",
                fato_verificado=(
                    "Saldo financeiro do item igual a zero."
                ),
                evidencia=(
                    f"previsto={resumo.valor_previsto}; "
                    f"executado={resumo.valor_executado}."
                ),
                risco_glosa="",
                recomendacao=(
                    "Manter a conferência documental e material "
                    "da execução."
                ),
            )
        )

    elif resumo.valor_executado > 0:
        achados.append(
            ResultadoRegra(
                codigo="PT_ITEM_EXECUCAO_PARCIAL",
                severidade="info",
                titulo="Item parcialmente executado",
                descricao=(
                    "O item possui execução financeira inferior "
                    "ao total previsto."
                ),
                regra="PT_ITEM_EXECUCAO_PARCIAL",
                categoria="plano_execucao",
                resultado="informativo",
                fato_verificado=(
                    "Existe saldo financeiro disponível no item."
                ),
                evidencia=(
                    f"previsto={resumo.valor_previsto}; "
                    f"executado={resumo.valor_executado}; "
                    f"saldo={resumo.saldo}."
                ),
                risco_glosa="",
                recomendacao=(
                    "Acompanhar a execução acumulada do item."
                ),
            )
        )

    else:
        achados.append(
            ResultadoRegra(
                codigo="PT_ITEM_SEM_EXECUCAO",
                severidade="info",
                titulo="Item ainda sem execução financeira",
                descricao=(
                    "Não há lançamento ativo vinculado ao item."
                ),
                regra="PT_ITEM_SEM_EXECUCAO",
                categoria="plano_execucao",
                resultado="informativo",
                fato_verificado=(
                    "Valor executado igual a zero."
                ),
                evidencia=(
                    f"previsto={resumo.valor_previsto}."
                ),
                risco_glosa="",
                recomendacao=(
                    "Nenhuma providência financeira necessária "
                    "apenas por ausência de execução."
                ),
            )
        )

    return achados
