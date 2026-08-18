from dataclasses import dataclass, field

from apps.planos_trabalho.financeiro import (
    resumo_financeiro_item,
)
from apps.regras.context import ContextoRegras
from apps.regras.rules.plano_execucao import (
    avaliar_execucao_financeira_item,
)


@dataclass
class ResultadoExecucaoItemPlano:
    item_id: int
    resumo: object
    achados: list = field(default_factory=list)

    @property
    def criticos(self):
        return [
            item
            for item in self.achados
            if item.severidade == "critico"
        ]

    @property
    def alertas(self):
        return [
            item
            for item in self.achados
            if item.severidade == "alerta"
        ]

    @property
    def resultado_preliminar(self):
        if self.criticos:
            return "pendencia_critica"

        if self.alertas:
            return "requer_conferencia"

        return "sem_inconsistencia_relevante_detectada"


def analisar_execucao_item_plano(
    item,
    contexto=None,
):
    contexto = contexto or ContextoRegras()

    resumo = resumo_financeiro_item(
        item
    )

    achados = avaliar_execucao_financeira_item(
        resumo
    )

    return ResultadoExecucaoItemPlano(
        item_id=item.pk,
        resumo=resumo,
        achados=achados,
    )
