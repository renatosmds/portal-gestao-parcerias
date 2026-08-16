from apps.regras.context import FonteNormativa


LEI_13019_VIGENTE = FonteNormativa(
    codigo="BR_LEI_13019_2014",
    titulo="Lei Federal nº 13.019/2014 - texto vigente e alterações",
    escopo="nacional",
    referencia="MROSC - redação vigente/compilada",
    ente="Brasil",
)


def fontes_contagem():
    """
    Fontes exclusivas do tenant Município de Contagem/MG.

    Nunca utilizar estas referências para outro município,
    órgão ou entidade.
    """

    return (
        FonteNormativa(
            codigo="CONTAGEM_DEC_30_2017",
            titulo="Decreto Municipal nº 30/2017",
            escopo="municipal",
            referencia="Regulamentação municipal do MROSC",
            ente="Contagem/MG",
        ),
        FonteNormativa(
            codigo="CONTAGEM_MANUAL_PC",
            titulo="Manual de Prestação de Contas - Parcerias Voluntárias",
            escopo="orgao",
            referencia="Manual municipal de prestação de contas",
            ente="Contagem/MG",
        ),
    )


def contexto_normativo_base(*fontes_adicionais):
    """
    Retorna somente a camada nacional mais as fontes
    explicitamente fornecidas pelo tenant.
    """

    return (
        LEI_13019_VIGENTE,
        *fontes_adicionais,
    )

