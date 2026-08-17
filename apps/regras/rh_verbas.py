from dataclasses import dataclass, field

from apps.regras.context import ContextoRegras
from apps.regras.rules.rh_verbas import (
    avaliar_verbas_trabalhistas_rh,
)


@dataclass
class ResultadoVerbasRH:
    folha_pagamento_id: int
    funcionario_id: int
    competencia: object
    achados: list = field(default_factory=list)

    @property
    def total_achados(self):
        return len(self.achados)

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

        return "sem_inconsistencia_detectada"


def analisar_verbas_rh(folha, contexto=None):
    contexto = contexto or ContextoRegras()

    achados = avaliar_verbas_trabalhistas_rh(
        folha,
        contexto=contexto,
    )

    return ResultadoVerbasRH(
        folha_pagamento_id=folha.pk,
        funcionario_id=folha.funcionario_id,
        competencia=folha.competencia,
        achados=achados,
    )
