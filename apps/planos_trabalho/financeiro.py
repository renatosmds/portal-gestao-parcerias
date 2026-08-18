from dataclasses import dataclass
from decimal import Decimal

from django.db.models import Sum

from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    VinculoLancamentoItemPlano,
)


def _d(valor):
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01")
    )


@dataclass(frozen=True)
class ResumoFinanceiroItemPlano:
    item_id: int
    valor_previsto: Decimal
    valor_executado: Decimal
    saldo: Decimal
    percentual_execucao: Decimal
    quantidade_lancamentos: int

    @property
    def extrapolado(self):
        return self.valor_executado > self.valor_previsto

    @property
    def saldo_negativo(self):
        return self.saldo < 0


def resumo_financeiro_item(item):
    """
    Considera apenas vínculos ativos.

    O valor executado é obtido de valor_documento
    dos lançamentos atualmente vinculados ao item.
    """

    vinculos = (
        VinculoLancamentoItemPlano.objects
        .filter(
            item_plano=item,
            ativo=True,
        )
        .select_related("lancamento")
    )

    valor_previsto = _d(
        item.valor_total_previsto
    )

    valor_executado = Decimal("0.00")

    for vinculo in vinculos:
        valor_executado += _d(
            getattr(
                vinculo.lancamento,
                "valor_documento",
                None,
            )
        )

    valor_executado = valor_executado.quantize(
        Decimal("0.01")
    )

    saldo = (
        valor_previsto - valor_executado
    ).quantize(
        Decimal("0.01")
    )

    if valor_previsto > 0:
        percentual = (
            valor_executado
            / valor_previsto
            * Decimal("100")
        ).quantize(
            Decimal("0.01")
        )
    else:
        percentual = Decimal("0.00")

    return ResumoFinanceiroItemPlano(
        item_id=item.pk,
        valor_previsto=valor_previsto,
        valor_executado=valor_executado,
        saldo=saldo,
        percentual_execucao=percentual,
        quantidade_lancamentos=vinculos.count(),
    )


def resumo_financeiro_plano(plano):
    """
    Consolida os itens ativos da versão do Plano.
    """

    itens = (
        ItemPlanoTrabalho.objects
        .filter(
            plano=plano,
            ativo=True,
        )
        .order_by("codigo")
    )

    resumos = [
        resumo_financeiro_item(item)
        for item in itens
    ]

    previsto = sum(
        (
            item.valor_previsto
            for item in resumos
        ),
        Decimal("0.00"),
    )

    executado = sum(
        (
            item.valor_executado
            for item in resumos
        ),
        Decimal("0.00"),
    )

    saldo = (
        previsto - executado
    ).quantize(
        Decimal("0.01")
    )

    return {
        "plano_id": plano.pk,
        "valor_previsto": previsto.quantize(
            Decimal("0.01")
        ),
        "valor_executado": executado.quantize(
            Decimal("0.01")
        ),
        "saldo": saldo,
        "itens": resumos,
    }
