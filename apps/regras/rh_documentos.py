from dataclasses import dataclass, field

from apps.regras.context import ContextoRegras
from apps.regras.rules.rh_documentos import avaliar_documentacao_rh


@dataclass
class ResultadoDocumentacaoRH:
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
    def informativos(self):
        return [
            item
            for item in self.achados
            if item.severidade == "info"
        ]

    @property
    def resultado_preliminar(self):
        if self.criticos:
            return "pendencia_critica"

        if self.alertas:
            return "documentacao_incompleta"

        return "documentacao_localizada"


def analisar_documentacao_rh(folha, contexto=None):
    contexto = contexto or ContextoRegras()

    achados = avaliar_documentacao_rh(
        folha,
        contexto=contexto,
    )

    return ResultadoDocumentacaoRH(
        folha_pagamento_id=folha.pk,
        funcionario_id=folha.funcionario_id,
        competencia=folha.competencia,
        achados=achados,
    )
