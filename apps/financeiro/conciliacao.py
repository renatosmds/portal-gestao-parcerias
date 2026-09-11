from datetime import timedelta
from decimal import Decimal

from apps.lancamentos.models import Lancamento

from .models import (
    ConciliacaoFinanceira,
    MovimentacaoFinanceira,
)


class StatusConciliacao:
    NAO_APLICAVEL = "nao_aplicavel"
    SEM_CORRESPONDENCIA = "sem_correspondencia"
    EXATO = "exato"
    PROVAVEL = "provavel"
    AMBIGUO = "ambiguo"


TIPOS_CONCILIAVEIS_COM_LANCAMENTO = {
    MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
}


ROTULOS_STATUS_CONCILIACAO = {
    StatusConciliacao.NAO_APLICAVEL: "Nao aplicavel",
    StatusConciliacao.SEM_CORRESPONDENCIA: "Sem correspondencia",
    StatusConciliacao.EXATO: "Correspondencia exata",
    StatusConciliacao.PROVAVEL: "Correspondencia provavel",
    StatusConciliacao.AMBIGUO: "Correspondencia ambigua",
}


def buscar_candidatos_lancamento(
    movimentacao,
    tolerancia_dias=3,
):
    resultado = {
        "status": StatusConciliacao.NAO_APLICAVEL,
        "movimentacao": movimentacao,
        "candidatos": [],
        "candidato": None,
    }

    if (
        movimentacao.tipo
        not in TIPOS_CONCILIAVEIS_COM_LANCAMENTO
    ):
        return resultado

    if not movimentacao.competencia_id:
        resultado["status"] = (
            StatusConciliacao.SEM_CORRESPONDENCIA
        )
        return resultado

    queryset = (
        Lancamento.objects
        .filter(
            empresa_id=movimentacao.empresa_id,
            termo_id=movimentacao.termo_id,
            prestacao_id=movimentacao.prestacao_id,
            competencia_id=movimentacao.competencia_id,
            valor_documento=movimentacao.valor,
        )
        .order_by(
            "data_pagamento",
            "id",
        )
    )

    exatos = list(
        queryset.filter(
            data_pagamento=movimentacao.data
        )
    )

    if len(exatos) == 1:
        resultado["status"] = (
            StatusConciliacao.EXATO
        )
        resultado["candidatos"] = exatos
        resultado["candidato"] = exatos[0]
        return resultado

    if len(exatos) > 1:
        resultado["status"] = (
            StatusConciliacao.AMBIGUO
        )
        resultado["candidatos"] = exatos
        return resultado

    data_inicial = (
        movimentacao.data
        - timedelta(days=tolerancia_dias)
    )
    data_final = (
        movimentacao.data
        + timedelta(days=tolerancia_dias)
    )

    proximos = list(
        queryset.filter(
            data_pagamento__range=(
                data_inicial,
                data_final,
            )
        )
    )

    if len(proximos) == 1:
        resultado["status"] = (
            StatusConciliacao.PROVAVEL
        )
        resultado["candidatos"] = proximos
        resultado["candidato"] = proximos[0]
        return resultado

    if len(proximos) > 1:
        resultado["status"] = (
            StatusConciliacao.AMBIGUO
        )
        resultado["candidatos"] = proximos
        return resultado

    resultado["status"] = (
        StatusConciliacao.SEM_CORRESPONDENCIA
    )

    return resultado


def resumo_conciliacao_competencia(competencia):
    movimentacoes = (
        MovimentacaoFinanceira.objects
        .filter(
            competencia=competencia,
            tipo__in=TIPOS_CONCILIAVEIS_COM_LANCAMENTO,
        )
        .order_by(
            "data",
            "id",
        )
    )

    movimentacoes = list(
        movimentacoes
    )

    decisoes = {
        item.movimentacao_id: item
        for item in (
            ConciliacaoFinanceira.objects
            .filter(
                movimentacao__in=movimentacoes
            )
            .select_related(
                "lancamento",
                "decidido_por",
            )
        )
    }

    itens = []

    for movimentacao in movimentacoes:
        resultado = buscar_candidatos_lancamento(
            movimentacao
        )

        decisao = decisoes.get(
            movimentacao.pk
        )

        resultado["decisao_manual"] = (
            decisao
        )

        resultado["status_manual"] = (
            decisao.status
            if decisao
            else None
        )

        itens.append(resultado)

    correspondencias_exatas = {}

    for item in itens:
        if (
            item["status"]
            != StatusConciliacao.EXATO
            or item["candidato"] is None
        ):
            continue

        candidato_id = item[
            "candidato"
        ].pk

        correspondencias_exatas.setdefault(
            candidato_id,
            [],
        ).append(item)

    for grupo in correspondencias_exatas.values():
        if len(grupo) <= 1:
            continue

        for item in grupo:
            item["status"] = (
                StatusConciliacao.AMBIGUO
            )

            item["candidato"] = None

    totais = {
        StatusConciliacao.EXATO: 0,
        StatusConciliacao.PROVAVEL: 0,
        StatusConciliacao.AMBIGUO: 0,
        StatusConciliacao.SEM_CORRESPONDENCIA: 0,
    }

    for item in itens:
        status = item["status"]

        if status in totais:
            totais[status] += 1

        item["rotulo_status"] = (
            ROTULOS_STATUS_CONCILIACAO.get(
                status,
                status,
            )
        )

    total = len(itens)

    conciliaveis = (
        totais[StatusConciliacao.EXATO]
        + totais[StatusConciliacao.PROVAVEL]
    )

    pendentes = (
        totais[StatusConciliacao.AMBIGUO]
        + totais[
            StatusConciliacao.SEM_CORRESPONDENCIA
        ]
    )

    confirmados = sum(
        1
        for item in itens
        if item["status_manual"]
        == ConciliacaoFinanceira.Status.CONFIRMADO
    )

    rejeitados = sum(
        1
        for item in itens
        if item["status_manual"]
        == ConciliacaoFinanceira.Status.REJEITADO
    )

    nao_analisados = (
        total
        - confirmados
        - rejeitados
    )

    return {
        "total": total,
        "confirmados": confirmados,
        "rejeitados": rejeitados,
        "nao_analisados": nao_analisados,
        "exatos": totais[
            StatusConciliacao.EXATO
        ],
        "provaveis": totais[
            StatusConciliacao.PROVAVEL
        ],
        "ambiguos": totais[
            StatusConciliacao.AMBIGUO
        ],
        "sem_correspondencia": totais[
            StatusConciliacao.SEM_CORRESPONDENCIA
        ],
        "conciliaveis": conciliaveis,
        "pendentes": pendentes,
        "itens": itens,
    }
