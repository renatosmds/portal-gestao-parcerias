from dataclasses import dataclass, field

from apps.regras.context import ContextoRegras
from apps.regras.rules.rh import avaliar_folha_pagamento


@dataclass
class ResultadoAnaliseRH:
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
    def possui_risco_glosa(self):
        return any(
            bool(item.risco_glosa)
            for item in self.achados
        )

    @property
    def resultado_preliminar(self):
        """
        Resultado técnico preliminar.

        Não representa aprovação, reprovação ou glosa administrativa.
        """
        if self.criticos:
            return "pendencia_critica"

        if self.alertas:
            return "requer_conferencia"

        return "sem_inconsistencia_detectada"


def analisar_folha_pagamento(folha, contexto=None):
    contexto = contexto or ContextoRegras()

    achados = avaliar_folha_pagamento(
        folha,
        contexto=contexto,
    )

    return ResultadoAnaliseRH(
        folha_pagamento_id=folha.pk,
        funcionario_id=folha.funcionario_id,
        competencia=folha.competencia,
        achados=achados,
    )
