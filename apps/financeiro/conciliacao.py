from django.db.models import Count
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


def movimento_integralmente_estornado(movimentacao):
    if (
        movimentacao.tipo
        != MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO
    ):
        return False

    if not movimentacao.pk:
        return False

    return (
        movimentacao.movimentos_relacionados
        .filter(
            tipo=MovimentacaoFinanceira.Tipo.ESTORNO,
            valor=movimentacao.valor,
        )
        .exists()
    )


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

    if movimento_integralmente_estornado(
        movimentacao
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


    movimentacoes = [
        movimentacao
        for movimentacao in movimentacoes
        if not movimento_integralmente_estornado(
            movimentacao
        )
    ]

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


def diagnostico_conciliacao_competencia(
    competencia,
):
    movimentacoes = list(
        MovimentacaoFinanceira.objects
        .filter(
            competencia=competencia,
            tipo=(
                MovimentacaoFinanceira.Tipo
                .DEBITO_AUTORIZADO
            ),
        )
        .order_by(
            "data",
            "id",
        )
    )

    movimentacoes = [
        movimento
        for movimento in movimentacoes
        if not movimento_integralmente_estornado(
            movimento
        )
    ]

    lancamentos = list(
        Lancamento.objects
        .filter(
            competencia=competencia,
            empresa_id=competencia.prestacao.empresa_id,
            prestacao=competencia.prestacao,
        )
        .order_by(
            "data_pagamento",
            "id",
        )
    )


    lancamentos_prestacao = (
        Lancamento.objects
        .filter(
            prestacao=competencia.prestacao,
            empresa_id=competencia.prestacao.empresa_id,
        )
    )

    total_lancamentos_prestacao = (
        lancamentos_prestacao.count()
    )

    lancamentos_sem_competencia = (
        lancamentos_prestacao
        .filter(
            competencia__isnull=True
        )
        .count()
    )

    lancamentos_outras_competencias = (
        lancamentos_prestacao
        .exclude(
            competencia=competencia
        )
        .exclude(
            competencia__isnull=True
        )
        .count()
    )

    distribuicao_competencias = list(
        lancamentos_prestacao
        .exclude(
            competencia__isnull=True
        )
        .values(
            "competencia__ano",
            "competencia__mes",
        )
        .annotate(
            total=Count("id")
        )
        .order_by(
            "competencia__ano",
            "competencia__mes",
        )
    )


    detalhes_lancamentos_prestacao = list(
        lancamentos_prestacao
        .select_related(
            "competencia"
        )
        .values(
            "id",
            "numero_lancamento",
            "data_documento",
            "data_pagamento",
            "valor_documento",
            "competencia__ano",
            "competencia__mes",
        )
        .order_by(
            "competencia__ano",
            "competencia__mes",
            "data_pagamento",
            "id",
        )[:20]
    )

    com_data_pagamento = [
        lancamento
        for lancamento in lancamentos
        if lancamento.data_pagamento
    ]

    sem_data_pagamento = (
        len(lancamentos)
        - len(com_data_pagamento)
    )

    mesma_data = 0
    ate_3_dias = 0
    ate_7_dias = 0
    ate_15_dias = 0
    acima_15_dias = 0
    valor_existente = 0
    sem_mesmo_valor = 0

    exemplos_sem_valor = []

    for movimento in movimentacoes:
        candidatos_valor = [
            lancamento
            for lancamento in lancamentos
            if lancamento.valor_documento
            == movimento.valor
        ]

        if not candidatos_valor:
            sem_mesmo_valor += 1

            if len(exemplos_sem_valor) < 10:
                exemplos_sem_valor.append(
                    {
                        "movimentacao_id": (
                            movimento.pk
                        ),
                        "data": movimento.data,
                        "valor": movimento.valor,
                        "descricao": (
                            movimento.memo_ofx
                            or movimento.descricao
                            or ""
                        ),
                    }
                )

            continue

        valor_existente += 1

        candidatos_com_data = [
            lancamento
            for lancamento in candidatos_valor
            if lancamento.data_pagamento
        ]

        if not candidatos_com_data:
            continue

        menor_diferenca = min(
            abs(
                (
                    lancamento.data_pagamento
                    - movimento.data
                ).days
            )
            for lancamento
            in candidatos_com_data
        )

        if menor_diferenca == 0:
            mesma_data += 1
        elif menor_diferenca <= 3:
            ate_3_dias += 1
        elif menor_diferenca <= 7:
            ate_7_dias += 1
        elif menor_diferenca <= 15:
            ate_15_dias += 1
        else:
            acima_15_dias += 1

    datas_movimentos = [
        movimento.data
        for movimento in movimentacoes
    ]

    datas_lancamentos = [
        lancamento.data_pagamento
        for lancamento in com_data_pagamento
    ]

    return {
        "total_debitos": len(
            movimentacoes
        ),
        "total_lancamentos": len(
            lancamentos
        ),
        "total_lancamentos_prestacao": (
            total_lancamentos_prestacao
        ),
        "lancamentos_sem_competencia": (
            lancamentos_sem_competencia
        ),
        "lancamentos_outras_competencias": (
            lancamentos_outras_competencias
        ),
        "distribuicao_competencias": (
            distribuicao_competencias
        ),
        "detalhes_lancamentos_prestacao": (
            detalhes_lancamentos_prestacao
        ),
        "lancamentos_sem_data_pagamento": (
            sem_data_pagamento
        ),
        "valor_existente": valor_existente,
        "sem_mesmo_valor": sem_mesmo_valor,
        "mesma_data": mesma_data,
        "ate_3_dias": ate_3_dias,
        "ate_7_dias": ate_7_dias,
        "ate_15_dias": ate_15_dias,
        "acima_15_dias": acima_15_dias,
        "data_inicial_debitos": (
            min(datas_movimentos)
            if datas_movimentos
            else None
        ),
        "data_final_debitos": (
            max(datas_movimentos)
            if datas_movimentos
            else None
        ),
        "data_inicial_lancamentos": (
            min(datas_lancamentos)
            if datas_lancamentos
            else None
        ),
        "data_final_lancamentos": (
            max(datas_lancamentos)
            if datas_lancamentos
            else None
        ),
        "exemplos_sem_mesmo_valor": (
            exemplos_sem_valor
        ),
    }
