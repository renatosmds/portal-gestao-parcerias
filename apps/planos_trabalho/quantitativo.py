from dataclasses import dataclass
from decimal import Decimal

from apps.planos_trabalho.models import (
    VinculoLancamentoItemPlano,
)


def _d(valor, casas="0.00"):
    return Decimal(str(valor or 0)).quantize(
        Decimal(casas)
    )


@dataclass(frozen=True)
class ResumoQuantitativoItemPlano:
    item_id: int

    quantidade_prevista: object
    quantidade_executada: Decimal
    saldo_quantidade: object

    valor_unitario_previsto: object
    maior_valor_unitario_executado: object

    valor_calculado_execucao: Decimal

    quantidade_vinculos: int
    vinculos_sem_quantidade: int
    vinculos_sem_valor_unitario: int
    divergencias_valor_documento: int

    @property
    def quantidade_excedida(self):
        return (
            self.quantidade_prevista is not None
            and self.quantidade_executada
            > self.quantidade_prevista
        )

    @property
    def valor_unitario_excedido(self):
        return (
            self.valor_unitario_previsto is not None
            and self.maior_valor_unitario_executado is not None
            and self.maior_valor_unitario_executado
            > self.valor_unitario_previsto
        )


def resumo_quantitativo_item(item):
    vinculos = list(
        VinculoLancamentoItemPlano.objects
        .filter(
            item_plano=item,
            ativo=True,
        )
        .select_related("lancamento")
    )

    quantidade_prevista = (
        item.quantidade_prevista
    )

    valor_unitario_previsto = (
        item.valor_unitario_previsto
    )

    quantidade_executada = Decimal("0.0000")
    valor_calculado = Decimal("0.00")

    valores_unitarios = []

    sem_quantidade = 0
    sem_valor_unitario = 0
    divergencias_documento = 0

    for vinculo in vinculos:

        if vinculo.quantidade_executada is None:
            sem_quantidade += 1
        else:
            quantidade_executada += (
                vinculo.quantidade_executada
            )

        if vinculo.valor_unitario_executado is None:
            sem_valor_unitario += 1
        else:
            valores_unitarios.append(
                vinculo.valor_unitario_executado
            )

        calculado = (
            vinculo.valor_calculado_execucao
        )

        if calculado is not None:
            valor_calculado += calculado

            valor_documento = _d(
                getattr(
                    vinculo.lancamento,
                    "valor_documento",
                    None,
                )
            )

            if calculado != valor_documento:
                divergencias_documento += 1

    quantidade_executada = (
        quantidade_executada.quantize(
            Decimal("0.0000")
        )
    )

    valor_calculado = valor_calculado.quantize(
        Decimal("0.01")
    )

    if quantidade_prevista is not None:
        saldo_quantidade = (
            quantidade_prevista
            - quantidade_executada
        ).quantize(
            Decimal("0.0000")
        )
    else:
        saldo_quantidade = None

    maior_valor_unitario = (
        max(valores_unitarios)
        if valores_unitarios
        else None
    )

    return ResumoQuantitativoItemPlano(
        item_id=item.pk,
        quantidade_prevista=quantidade_prevista,
        quantidade_executada=quantidade_executada,
        saldo_quantidade=saldo_quantidade,
        valor_unitario_previsto=valor_unitario_previsto,
        maior_valor_unitario_executado=maior_valor_unitario,
        valor_calculado_execucao=valor_calculado,
        quantidade_vinculos=len(vinculos),
        vinculos_sem_quantidade=sem_quantidade,
        vinculos_sem_valor_unitario=sem_valor_unitario,
        divergencias_valor_documento=divergencias_documento,
    )
