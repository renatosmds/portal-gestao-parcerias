from decimal import Decimal

from django.db.models import Sum

from apps.lancamentos.models import Lancamento

from .conciliacao import (
    StatusConciliacao,
    buscar_candidatos_lancamento,
)
from .models import MovimentacaoFinanceira


ZERO = Decimal("0.00")


def _somar_movimentacoes(queryset, tipo):
    resultado = (
        queryset
        .filter(tipo=tipo)
        .aggregate(
            total=Sum(
                "valor",
                default=ZERO,
            )
        )
    )

    return resultado.get("total") or ZERO


def resumo_financeiro_competencia(competencia):
    movimentacoes = (
        MovimentacaoFinanceira.objects
        .filter(
            competencia=competencia
        )
    )

    lancamentos = (
        Lancamento.objects
        .filter(
            competencia=competencia
        )
    )

    repasse = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.REPASSE,
    )

    deposito_osc = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.DEPOSITO_OSC,
    )

    rendimento = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.RENDIMENTO,
    )

    credito_autorizado = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.CREDITO_AUTORIZADO,
    )

    resgate_automatico = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.RESGATE_AUTOMATICO,
    )

    estorno = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.ESTORNO,
    )

    aplicacao = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.APLICACAO,
    )

    debito_autorizado = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
    )

    debitos_autorizados = (
        movimentacoes
        .filter(
            tipo=(
                MovimentacaoFinanceira.Tipo
                .DEBITO_AUTORIZADO
            )
        )
        .order_by(
            "data",
            "id",
        )
    )

    debito_autorizado_conciliado = ZERO

    for movimento in debitos_autorizados:
        resultado = buscar_candidatos_lancamento(
            movimento
        )

        if (
            resultado["status"]
            == StatusConciliacao.EXATO
        ):
            debito_autorizado_conciliado += (
                movimento.valor
            )

    debito_autorizado_pendente = (
        debito_autorizado
        - debito_autorizado_conciliado
    )

    despesa_bancaria = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.DESPESA_BANCARIA,
    )

    imposto_renda = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.IMPOSTO_RENDA,
    )

    iof = _somar_movimentacoes(
        movimentacoes,
        MovimentacaoFinanceira.Tipo.IOF,
    )

    valor_lancamentos = (
        lancamentos
        .aggregate(
            total=Sum(
                "valor_documento",
                default=ZERO,
            )
        )
        .get("total")
        or ZERO
    )

    receita_total = (
        repasse
        + deposito_osc
        + rendimento
        + credito_autorizado
        + estorno
    )

    despesa_total = (
        debito_autorizado_pendente
        + despesa_bancaria
        + imposto_renda
        + iof
        + valor_lancamentos
    )

    total_entradas = (
        receita_total
        + resgate_automatico
    )

    total_saidas = (
        aplicacao
        + debito_autorizado_pendente
        + despesa_bancaria
        + imposto_renda
        + iof
        + valor_lancamentos
    )

    movimento_financeiro = (
        total_entradas
        - total_saidas
    )

    saldo_final_calculado = (
        competencia.saldo_inicial
        + movimento_financeiro
    )

    diferenca_saldo = (
        competencia.saldo_final
        - saldo_final_calculado
    )

    return {
        "repasse": repasse,
        "deposito_osc": deposito_osc,
        "rendimento": rendimento,
        "credito_autorizado": credito_autorizado,
        "resgate_automatico": resgate_automatico,
        "estorno": estorno,
        "aplicacao": aplicacao,
        "debito_autorizado": debito_autorizado,
        "debito_autorizado_conciliado": (
            debito_autorizado_conciliado
        ),
        "debito_autorizado_pendente": (
            debito_autorizado_pendente
        ),
        "despesa_bancaria": despesa_bancaria,
        "imposto_renda": imposto_renda,
        "iof": iof,
        "valor_lancamentos": valor_lancamentos,
        "receita_total": receita_total,
        "despesa_total": despesa_total,
        "total_entradas": total_entradas,
        "total_saidas": total_saidas,
        "movimento_financeiro": movimento_financeiro,
        "saldo_inicial": competencia.saldo_inicial,
        "saldo_final_calculado": saldo_final_calculado,
        "saldo_final_informado": competencia.saldo_final,
        "diferenca_saldo": diferenca_saldo,
        "conciliado": diferenca_saldo == ZERO,
    }
