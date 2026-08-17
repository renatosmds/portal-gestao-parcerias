from dataclasses import dataclass, field
from decimal import Decimal

from apps.regras.context import ContextoRegras
from apps.regras.rh import analisar_folha_pagamento
from apps.regras.rh_composicao import analisar_composicao_rh
from apps.regras.rh_conciliacao import analisar_conciliacao_rh
from apps.regras.rh_documentos import analisar_documentacao_rh
from apps.regras.rh_verbas import analisar_verbas_rh
from apps.regras.lgpd_rh import analisar_lgpd_rh


ORDEM_SEVERIDADE = {
    "critico": 0,
    "alerta": 1,
    "info": 2,
}


def _deduplicar_achados(achados):
    """
    Remove duplicidades estritas sem perder achados distintos
    que eventualmente utilizem o mesmo código.
    """
    unicos = []
    chaves = set()

    for item in achados:
        chave = (
            item.codigo,
            item.categoria,
            item.severidade,
            item.evidencia,
        )

        if chave in chaves:
            continue

        chaves.add(chave)
        unicos.append(item)

    return unicos


def _ordenar_achados(achados):
    return sorted(
        achados,
        key=lambda item: (
            ORDEM_SEVERIDADE.get(
                item.severidade,
                99,
            ),
            item.categoria,
            item.codigo,
        ),
    )


@dataclass
class ResultadoAnaliseTecnicaRH:
    folha_pagamento_id: int
    funcionario_id: int
    competencia: object

    analise_folha: object
    analise_documental: object
    analise_conciliacao: object
    analise_composicao: object
    analise_verbas: object
    analise_lgpd: object

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
    def total_criticos(self):
        return len(self.criticos)

    @property
    def total_alertas(self):
        return len(self.alertas)

    @property
    def total_informativos(self):
        return len(self.informativos)

    @property
    def categorias_afetadas(self):
        return sorted(
            {
                item.categoria
                for item in self.achados
                if item.severidade in {
                    "critico",
                    "alerta",
                }
            }
        )

    @property
    def pendencias_prioritarias(self):
        """
        Pendências em ordem de gravidade.

        Achados meramente informativos não entram na fila de
        pendências que exigem providência.
        """
        return [
            item
            for item in self.achados
            if item.severidade in {
                "critico",
                "alerta",
            }
        ]

    @property
    def possui_risco_glosa(self):
        return any(
            bool(item.risco_glosa)
            for item in self.pendencias_prioritarias
        )

    @property
    def possui_risco_lgpd_elevado(self):
        return any(
            item.categoria == "lgpd_rh"
            and item.severidade == "critico"
            for item in self.achados
        )

    @property
    def composicao_possui_ambiguidade_rescisoria(self):
        return any(
            item.codigo
            == "RH_RESCISAO_TOTAL_E_COMPONENTES_PRESENTES"
            for item in self.achados
        )

    @property
    def valor_potencialmente_elegivel(self):
        return (
            self.analise_composicao
            .composicao
            .valor_potencialmente_elegivel
        )

    @property
    def valor_lancado_identificado(self):
        return (
            self.analise_composicao
            .valor_lancado
        )

    @property
    def valor_potencial_confiavel_para_decisao(self):
        """
        O valor continua sendo apenas referência técnica.

        False significa que existe ambiguidade conhecida que
        impede seu uso isolado até conferência humana.
        """
        if self.composicao_possui_ambiguidade_rescisoria:
            return False

        return True

    @property
    def resultado_preliminar(self):
        if self.criticos:
            return "pendencia_critica"

        if self.alertas:
            return "requer_conferencia"

        return "sem_inconsistencia_relevante_detectada"

    @property
    def conclusao_executiva(self):
        """
        Conclusão executiva preliminar.

        Não representa aprovação, reprovação ou aplicação de glosa.
        """
        if self.criticos:
            return (
                "Foram identificadas pendências críticas na análise "
                "de recursos humanos. A despesa não deve ser considerada "
                "tecnicamente concluída sem conferência e saneamento "
                "dos achados apontados."
            )

        if self.alertas:
            return (
                "Não foram identificadas pendências críticas, porém "
                "existem pontos que requerem conferência documental, "
                "financeira, trabalhista ou de privacidade antes da "
                "conclusão da análise."
            )

        return (
            "Com base nos dados disponíveis e nas regras automatizadas "
            "executadas, não foram detectadas inconsistências relevantes. "
            "O resultado é preliminar e permanece sujeito à conferência "
            "humana, ao Plano de Trabalho e às normas aplicáveis."
        )

    def resumo_executivo(self):
        return {
            "resultado_preliminar": self.resultado_preliminar,
            "total_achados": self.total_achados,
            "criticos": self.total_criticos,
            "alertas": self.total_alertas,
            "informativos": self.total_informativos,
            "categorias_afetadas": self.categorias_afetadas,
            "possui_risco_glosa": self.possui_risco_glosa,
            "possui_risco_lgpd_elevado": (
                self.possui_risco_lgpd_elevado
            ),
            "valor_potencialmente_elegivel": str(
                self.valor_potencialmente_elegivel
            ),
            "valor_lancado_identificado": str(
                self.valor_lancado_identificado
            ),
            "valor_potencial_confiavel_para_decisao": (
                self.valor_potencial_confiavel_para_decisao
            ),
            "conclusao_executiva": self.conclusao_executiva,
        }


def analisar_rh_completo(
    folha,
    contexto=None,
    *,
    uso_ia=False,
    dados_minimizados=False,
):
    contexto = contexto or ContextoRegras()

    analise_folha = analisar_folha_pagamento(
        folha,
        contexto=contexto,
    )

    analise_documental = analisar_documentacao_rh(
        folha,
        contexto=contexto,
    )

    analise_conciliacao = analisar_conciliacao_rh(
        folha,
        contexto=contexto,
    )

    analise_composicao = analisar_composicao_rh(
        folha,
        contexto=contexto,
    )

    analise_verbas = analisar_verbas_rh(
        folha,
        contexto=contexto,
    )

    analise_lgpd = analisar_lgpd_rh(
        funcionario=folha.funcionario,
        contexto=contexto,
        uso_ia=uso_ia,
        dados_minimizados=dados_minimizados,
    )

    todos_achados = (
        list(analise_folha.achados)
        + list(analise_documental.achados)
        + list(analise_conciliacao.achados)
        + list(analise_composicao.achados)
        + list(analise_verbas.achados)
        + list(analise_lgpd.achados)
    )

    achados = _ordenar_achados(
        _deduplicar_achados(
            todos_achados
        )
    )

    return ResultadoAnaliseTecnicaRH(
        folha_pagamento_id=folha.pk,
        funcionario_id=folha.funcionario_id,
        competencia=folha.competencia,

        analise_folha=analise_folha,
        analise_documental=analise_documental,
        analise_conciliacao=analise_conciliacao,
        analise_composicao=analise_composicao,
        analise_verbas=analise_verbas,
        analise_lgpd=analise_lgpd,

        achados=achados,
    )
