from apps.regras.resultado import ResultadoRegra


def avaliar_meta_objeto_item(resumo):
    achados = []

    if not resumo.possui_meta:
        achados.append(
            ResultadoRegra(
                codigo="PT_ITEM_SEM_META_VINCULADA",
                severidade="alerta",
                titulo="Item sem meta vinculada",
                descricao=(
                    "O item do Plano de Trabalho possui "
                    "execução estruturada, mas não está "
                    "vinculado a uma meta."
                ),
                regra="PT_ITEM_SEM_META_VINCULADA",
                categoria="plano_meta_objeto",
                resultado="nao_verificado",
                fato_verificado=(
                    "Não existe MetaExecucao associada "
                    "ao item."
                ),
                evidencia=(
                    f"item_id={resumo.item_id}; "
                    f"lancamentos="
                    f"{resumo.quantidade_lancamentos}."
                ),
                risco_glosa=(
                    "Indeterminado. A ausência do vínculo "
                    "reduz a rastreabilidade entre despesa "
                    "e resultado pactuado."
                ),
                recomendacao=(
                    "Identificar a meta correspondente no "
                    "Plano de Trabalho antes de concluir "
                    "a análise da execução."
                ),
            )
        )

        return achados

    if resumo.empresa_compativel is False:
        achados.append(
            ResultadoRegra(
                codigo="PT_META_EMPRESA_INCOMPATIVEL",
                severidade="critico",
                titulo="Meta vinculada a outra OSC",
                descricao=(
                    "A prestação associada à meta pertence "
                    "a empresa diferente daquela vinculada "
                    "ao Termo do item."
                ),
                regra="PT_META_EMPRESA_INCOMPATIVEL",
                categoria="plano_meta_objeto",
                resultado="achado",
                fato_verificado=(
                    "A empresa da prestação da meta diverge "
                    "da empresa do Termo."
                ),
                evidencia=(
                    f"empresa_termo="
                    f"{resumo.termo_empresa_id}; "
                    f"empresa_prestacao="
                    f"{resumo.prestacao_empresa_id}."
                ),
                risco_glosa=(
                    "Elevado quanto à rastreabilidade. "
                    "O vínculo pode ter sido realizado "
                    "com meta de outra parceria."
                ),
                recomendacao=(
                    "Corrigir ou justificar o vínculo antes "
                    "da conclusão da análise."
                ),
            )
        )

    elif resumo.empresa_compativel is None:
        achados.append(
            ResultadoRegra(
                codigo="PT_META_EMPRESA_NAO_VERIFICAVEL",
                severidade="alerta",
                titulo="OSC da meta não verificável",
                descricao=(
                    "Não existem dados estruturados suficientes "
                    "para confirmar a identidade entre a OSC "
                    "do Termo e a prestação da meta."
                ),
                regra="PT_META_EMPRESA_NAO_VERIFICAVEL",
                categoria="plano_meta_objeto",
                resultado="nao_verificado",
                fato_verificado=(
                    "A validação por empresa ficou inconclusiva."
                ),
                evidencia="",
                risco_glosa=(
                    "Indeterminado até confirmação documental."
                ),
                recomendacao=(
                    "Conferir a prestação e o Termo associados."
                ),
            )
        )

    if resumo.numero_termo_compativel is False:
        achados.append(
            ResultadoRegra(
                codigo="PT_META_TERMO_INCOMPATIVEL",
                severidade="critico",
                titulo="Meta vinculada a outro Termo",
                descricao=(
                    "O número do Termo informado na prestação "
                    "da meta é diferente do Termo associado "
                    "ao item do Plano."
                ),
                regra="PT_META_TERMO_INCOMPATIVEL",
                categoria="plano_meta_objeto",
                resultado="achado",
                fato_verificado=(
                    "Foi identificada divergência entre os "
                    "identificadores da parceria."
                ),
                evidencia=(
                    f"termo_item='{resumo.termo_numero}'; "
                    f"termo_prestacao="
                    f"'{resumo.prestacao_numtermo}'."
                ),
                risco_glosa=(
                    "Elevado quanto à rastreabilidade da "
                    "despesa com a parceria correta."
                ),
                recomendacao=(
                    "Revisar imediatamente a meta vinculada "
                    "e confirmar a prestação correspondente."
                ),
            )
        )

    elif resumo.numero_termo_compativel is None:
        achados.append(
            ResultadoRegra(
                codigo="PT_META_TERMO_NAO_VERIFICAVEL",
                severidade="alerta",
                titulo="Termo da meta não verificável",
                descricao=(
                    "Não existem identificadores suficientes "
                    "para confirmar automaticamente se a "
                    "prestação da meta corresponde ao Termo."
                ),
                regra="PT_META_TERMO_NAO_VERIFICAVEL",
                categoria="plano_meta_objeto",
                resultado="nao_verificado",
                fato_verificado=(
                    "Comparação do número do Termo inconclusiva."
                ),
                evidencia=(
                    f"termo_item='{resumo.termo_numero}'; "
                    f"termo_prestacao="
                    f"'{resumo.prestacao_numtermo}'."
                ),
                risco_glosa=(
                    "Indeterminado até conferência da parceria."
                ),
                recomendacao=(
                    "Conferir os documentos da parceria e "
                    "padronizar o número do Termo."
                ),
            )
        )

    if not (
        resumo.meta_titulo.strip()
        or resumo.meta_descricao.strip()
    ):
        achados.append(
            ResultadoRegra(
                codigo="PT_META_SEM_DESCRICAO_SUFICIENTE",
                severidade="alerta",
                titulo="Meta sem descrição suficiente",
                descricao=(
                    "A meta vinculada não possui conteúdo "
                    "textual suficiente para apoiar a análise "
                    "de compatibilidade da despesa."
                ),
                regra="PT_META_SEM_DESCRICAO_SUFICIENTE",
                categoria="plano_meta_objeto",
                resultado="nao_verificado",
                fato_verificado=(
                    "Título e descrição da meta não fornecem "
                    "informação útil para a comparação."
                ),
                evidencia=(
                    f"meta_id={resumo.meta_id}."
                ),
                risco_glosa=(
                    "Indeterminado. Trata-se de deficiência "
                    "de rastreabilidade, não de irregularidade "
                    "material automaticamente comprovada."
                ),
                recomendacao=(
                    "Conferir o Plano de Trabalho original "
                    "e complementar a descrição estruturada."
                ),
            )
        )

    if not resumo.objeto.strip():
        achados.append(
            ResultadoRegra(
                codigo="PT_TERMO_SEM_OBJETO_ESTRUTURADO",
                severidade="alerta",
                titulo="Objeto da parceria não estruturado",
                descricao=(
                    "O Termo não possui objeto preenchido "
                    "de forma estruturada para comparação "
                    "com a meta e a despesa."
                ),
                regra="PT_TERMO_SEM_OBJETO_ESTRUTURADO",
                categoria="plano_meta_objeto",
                resultado="nao_verificado",
                fato_verificado=(
                    "Campo objeto do Termo ausente ou vazio."
                ),
                evidencia=(
                    f"termo_id={resumo.termo_id}."
                ),
                risco_glosa=(
                    "Indeterminado até conferência do instrumento."
                ),
                recomendacao=(
                    "Conferir o Termo e registrar o objeto "
                    "da parceria de forma estruturada."
                ),
            )
        )

    estrutura_compativel = (
        resumo.empresa_compativel is True
        and resumo.numero_termo_compativel is True
    )

    if estrutura_compativel:
        achados.append(
            ResultadoRegra(
                codigo="PT_META_RASTREABILIDADE_CONFIRMADA",
                severidade="info",
                titulo="Rastreabilidade estrutural confirmada",
                descricao=(
                    "A meta vinculada pertence à mesma OSC "
                    "e ao mesmo número de Termo do item "
                    "analisado."
                ),
                regra="PT_META_RASTREABILIDADE_CONFIRMADA",
                categoria="plano_meta_objeto",
                resultado="informativo",
                fato_verificado=(
                    "Empresa e número do Termo são compatíveis."
                ),
                evidencia=(
                    f"meta_id={resumo.meta_id}; "
                    f"prestacao_id={resumo.prestacao_id}; "
                    f"lancamentos="
                    f"{resumo.quantidade_lancamentos}; "
                    f"valor_lancamentos="
                    f"{resumo.valor_lancamentos}."
                ),
                risco_glosa="",
                recomendacao=(
                    "Prosseguir com a análise material da "
                    "despesa, da meta e do objeto."
                ),
            )
        )

    if (
        resumo.tokens_despesa
        and resumo.tokens_meta
        and not resumo.possui_evidencia_textual_despesa_meta
    ):
        achados.append(
            ResultadoRegra(
                codigo="PT_DESPESA_META_SEM_EVIDENCIA_TEXTUAL",
                severidade="alerta",
                titulo="Despesa e meta exigem conferência material",
                descricao=(
                    "A comparação textual automática não "
                    "identificou elementos comuns suficientes "
                    "entre a despesa/item e a meta."
                ),
                regra="PT_DESPESA_META_SEM_EVIDENCIA_TEXTUAL",
                categoria="plano_meta_objeto",
                resultado="nao_verificado",
                fato_verificado=(
                    "Não houve coincidência lexical relevante "
                    "entre os textos estruturados."
                ),
                evidencia=(
                    "A ausência de palavras comuns não prova "
                    "incompatibilidade material."
                ),
                risco_glosa=(
                    "Não determinado por esta regra."
                ),
                recomendacao=(
                    "Analisar documentalmente se a despesa "
                    "contribui para o alcance da meta."
                ),
            )
        )

    if (
        resumo.tokens_meta
        and resumo.tokens_objeto
        and not resumo.possui_evidencia_textual_meta_objeto
    ):
        achados.append(
            ResultadoRegra(
                codigo="PT_META_OBJETO_SEM_EVIDENCIA_TEXTUAL",
                severidade="alerta",
                titulo="Meta e objeto exigem conferência material",
                descricao=(
                    "A comparação textual automática não "
                    "identificou elementos comuns suficientes "
                    "entre a meta e o objeto da parceria."
                ),
                regra="PT_META_OBJETO_SEM_EVIDENCIA_TEXTUAL",
                categoria="plano_meta_objeto",
                resultado="nao_verificado",
                fato_verificado=(
                    "Não houve coincidência lexical relevante."
                ),
                evidencia=(
                    "A análise é apenas indicativa e não "
                    "estabelece incompatibilidade jurídica "
                    "ou material."
                ),
                risco_glosa=(
                    "Não determinado por esta regra."
                ),
                recomendacao=(
                    "Conferir o Plano de Trabalho e verificar "
                    "materialmente a relação da meta com "
                    "o objeto pactuado."
                ),
            )
        )

    return achados
