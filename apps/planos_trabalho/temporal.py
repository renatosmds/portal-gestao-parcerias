from dataclasses import dataclass, field

from apps.planos_trabalho.models import (
    VinculoLancamentoItemPlano,
)
from apps.planos_trabalho.vinculos import (
    data_referencia_lancamento,
)


@dataclass(frozen=True)
class ExecucaoTemporalLancamento:
    vinculo_id: int
    lancamento_id: int
    data_referencia: object
    origem_data: str
    situacao_temporal: str


@dataclass(frozen=True)
class ResumoTemporalItemPlano:
    item_id: int
    inicio_previsto: object
    fim_previsto: object
    execucoes: tuple = field(
        default_factory=tuple
    )

    @property
    def quantidade_lancamentos(self):
        return len(self.execucoes)

    @property
    def sem_data(self):
        return [
            item
            for item in self.execucoes
            if item.situacao_temporal == "sem_data"
        ]

    @property
    def antes_periodo(self):
        return [
            item
            for item in self.execucoes
            if item.situacao_temporal == "antes"
        ]

    @property
    def depois_periodo(self):
        return [
            item
            for item in self.execucoes
            if item.situacao_temporal == "depois"
        ]

    @property
    def dentro_periodo(self):
        return [
            item
            for item in self.execucoes
            if item.situacao_temporal == "dentro"
        ]

    @property
    def fora_periodo(self):
        return (
            self.antes_periodo
            + self.depois_periodo
        )


def _origem_data(lancamento):
    if getattr(
        lancamento,
        "data_documento",
        None,
    ):
        return "documento"

    if getattr(
        lancamento,
        "data_pagamento",
        None,
    ):
        return "pagamento"

    return "indeterminada"


def resumo_temporal_item(item):
    vinculos = (
        VinculoLancamentoItemPlano.objects
        .filter(
            item_plano=item,
            ativo=True,
        )
        .select_related("lancamento")
        .order_by("lancamento_id")
    )

    inicio = item.inicio_execucao
    fim = item.fim_execucao

    execucoes = []

    for vinculo in vinculos:
        lancamento = vinculo.lancamento

        data_referencia = (
            data_referencia_lancamento(
                lancamento
            )
        )

        origem = _origem_data(
            lancamento
        )

        if not data_referencia:
            situacao = "sem_data"

        elif (
            inicio
            and data_referencia < inicio
        ):
            situacao = "antes"

        elif (
            fim
            and data_referencia > fim
        ):
            situacao = "depois"

        else:
            situacao = "dentro"

        execucoes.append(
            ExecucaoTemporalLancamento(
                vinculo_id=vinculo.pk,
                lancamento_id=lancamento.pk,
                data_referencia=data_referencia,
                origem_data=origem,
                situacao_temporal=situacao,
            )
        )

    return ResumoTemporalItemPlano(
        item_id=item.pk,
        inicio_previsto=inicio,
        fim_previsto=fim,
        execucoes=tuple(execucoes),
    )
