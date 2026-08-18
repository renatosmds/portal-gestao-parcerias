from dataclasses import dataclass, field

from apps.regras.plano_execucao import (
    analisar_execucao_item_plano,
)
from apps.regras.plano_meta_objeto import (
    analisar_meta_objeto_item,
)
from apps.regras.plano_quantitativo import (
    analisar_execucao_quantitativa_item,
)
from apps.regras.plano_temporal import (
    analisar_execucao_temporal_item,
)


ORDEM_SEVERIDADE = {
    "critico": 0,
    "alerta": 1,
    "info": 2,
}


def _deduplicar_achados(achados):
    unicos = {}
    ordem = []

    for achado in achados:
        chave = (
            achado.codigo,
            achado.evidencia,
        )

        if chave not in unicos:
            unicos[chave] = achado
            ordem.append(chave)

    return [
        unicos[chave]
        for chave in ordem
    ]


def _ordenar_achados(achados):
    return sorted(
        achados,
        key=lambda item: (
            ORDEM_SEVERIDADE.get(
                item.severidade,
                99,
            ),
            item.codigo,
        ),
    )


@dataclass
class ResultadoConsolidadoItemPlano:
    item_id: int
    item_codigo: str

    financeiro: object
    quantitativo: object
    temporal: object
    meta_objeto: object

    achados: list = field(
        default_factory=list
    )

    conclusao_executiva: str = ""

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
    def quantidade_criticos(self):
        return len(
            self.criticos
        )

    @property
    def quantidade_alertas(self):
        return len(
            self.alertas
        )

    @property
    def resultado_preliminar(self):
        if self.criticos:
            return "pendencia_critica"

        if self.alertas:
            return "requer_conferencia"

        return (
            "sem_inconsistencia_relevante_detectada"
        )

    @property
    def resumo_executivo(self):
        financeiro = (
            self.financeiro.resumo
        )

        quantitativo = (
            self.quantitativo.resumo
        )

        temporal = (
            self.temporal.resumo
        )

        meta_objeto = (
            self.meta_objeto.resumo
        )

        return {
            "item_id": self.item_id,

            "resultado_preliminar": (
                self.resultado_preliminar
            ),

            "pendencias_criticas": (
                self.quantidade_criticos
            ),

            "alertas": (
                self.quantidade_alertas
            ),

            "financeiro": {
                "valor_previsto": (
                    financeiro.valor_previsto
                ),
                "valor_executado": (
                    financeiro.valor_executado
                ),
                "saldo": (
                    financeiro.saldo
                ),
                "percentual_execucao": (
                    financeiro.percentual_execucao
                ),
            },

            "quantitativo": {
                "quantidade_prevista": (
                    quantitativo.quantidade_prevista
                ),
                "quantidade_executada": (
                    quantitativo.quantidade_executada
                ),
                "saldo_quantidade": (
                    quantitativo.saldo_quantidade
                ),
                "valor_unitario_previsto": (
                    quantitativo.valor_unitario_previsto
                ),
                "maior_valor_unitario_executado": (
                    quantitativo
                    .maior_valor_unitario_executado
                ),
            },

            "temporal": {
                "inicio_previsto": (
                    temporal.inicio_previsto
                ),
                "fim_previsto": (
                    temporal.fim_previsto
                ),
                "lancamentos": (
                    temporal.quantidade_lancamentos
                ),
                "fora_periodo": len(
                    temporal.fora_periodo
                ),
            },

            "meta_objeto": {
                "meta_id": (
                    meta_objeto.meta_id
                ),
                "meta_codigo": (
                    meta_objeto.meta_codigo
                ),
                "meta_situacao": (
                    meta_objeto.meta_situacao
                ),
                "rastreabilidade_empresa": (
                    meta_objeto.empresa_compativel
                ),
                "rastreabilidade_termo": (
                    meta_objeto.numero_termo_compativel
                ),
            },

            "conclusao_executiva": (
                self.conclusao_executiva
            ),
        }


def gerar_conclusao_executiva_item(
    resultado,
):
    financeiro = (
        resultado.financeiro.resumo
    )

    if resultado.criticos:
        return (
            "Foram identificadas pendências críticas "
            "na execução do item do Plano de Trabalho. "
            f"Valor previsto: R$ "
            f"{financeiro.valor_previsto}; "
            f"valor executado: R$ "
            f"{financeiro.valor_executado}; "
            f"saldo: R$ {financeiro.saldo}. "
            f"Há {len(resultado.criticos)} pendência(s) "
            "crítica(s) e "
            f"{len(resultado.alertas)} alerta(s). "
            "Recomenda-se análise técnica e documental "
            "antes da conclusão sobre a regularidade "
            "da despesa. Nenhuma glosa é aplicada "
            "automaticamente por esta análise."
        )

    if resultado.alertas:
        return (
            "A execução do item apresenta ponto(s) que "
            "requerem conferência técnica ou documental, "
            "sem irregularidade material conclusiva "
            "automaticamente identificada. "
            f"Valor previsto: R$ "
            f"{financeiro.valor_previsto}; "
            f"valor executado: R$ "
            f"{financeiro.valor_executado}; "
            f"saldo: R$ {financeiro.saldo}. "
            f"Foram registrados "
            f"{len(resultado.alertas)} alerta(s). "
            "A decisão final deve considerar os "
            "documentos da parceria, a versão aplicável "
            "do Plano de Trabalho e as justificativas "
            "apresentadas."
        )

    return (
        "Não foram identificadas inconsistências "
        "relevantes nas verificações automáticas "
        "financeira, quantitativa, temporal e de "
        "rastreabilidade do item. "
        f"Valor previsto: R$ "
        f"{financeiro.valor_previsto}; "
        f"valor executado: R$ "
        f"{financeiro.valor_executado}; "
        f"saldo: R$ {financeiro.saldo}. "
        "A conclusão não dispensa a conferência "
        "documental, material e normativa da "
        "prestação de contas."
    )


def analisar_item_plano_completo(
    item,
    contexto=None,
):
    financeiro = (
        analisar_execucao_item_plano(
            item,
            contexto=contexto,
        )
    )

    quantitativo = (
        analisar_execucao_quantitativa_item(
            item,
            contexto=contexto,
        )
    )

    temporal = (
        analisar_execucao_temporal_item(
            item,
            contexto=contexto,
        )
    )

    meta_objeto = (
        analisar_meta_objeto_item(
            item,
            contexto=contexto,
        )
    )

    todos_achados = [
        *financeiro.achados,
        *quantitativo.achados,
        *temporal.achados,
        *meta_objeto.achados,
    ]

    achados = _ordenar_achados(
        _deduplicar_achados(
            todos_achados
        )
    )

    resultado = (
        ResultadoConsolidadoItemPlano(
            item_id=item.pk,
            item_codigo=str(item.codigo or item.pk),
            financeiro=financeiro,
            quantitativo=quantitativo,
            temporal=temporal,
            meta_objeto=meta_objeto,
            achados=achados,
        )
    )

    resultado.conclusao_executiva = (
        gerar_conclusao_executiva_item(
            resultado
        )
    )

    return resultado
