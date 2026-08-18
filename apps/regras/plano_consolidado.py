from dataclasses import dataclass, field
from decimal import Decimal

from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
)
from apps.regras.plano_item_consolidado import (
    analisar_item_plano_completo,
)


ORDEM_SEVERIDADE = {
    "critico": 0,
    "alerta": 1,
    "info": 2,
}


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


@dataclass
class ResultadoConsolidadoPlanoTrabalho:
    plano_id: int
    versao: int

    itens: list = field(
        default_factory=list
    )

    achados: list = field(
        default_factory=list
    )

    valor_previsto: Decimal = Decimal("0.00")
    valor_executado: Decimal = Decimal("0.00")
    saldo: Decimal = Decimal("0.00")

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
    def itens_criticos(self):
        return [
            item
            for item in self.itens
            if item.criticos
        ]

    @property
    def itens_com_alerta(self):
        return [
            item
            for item in self.itens
            if item.alertas
        ]

    @property
    def quantidade_itens(self):
        return len(
            self.itens
        )

    @property
    def quantidade_itens_criticos(self):
        return len(
            self.itens_criticos
        )

    @property
    def quantidade_itens_com_alerta(self):
        return len(
            self.itens_com_alerta
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
    def percentual_execucao(self):
        if self.valor_previsto <= 0:
            return Decimal("0.00")

        return (
            self.valor_executado
            / self.valor_previsto
            * Decimal("100")
        ).quantize(
            Decimal("0.01")
        )

    @property
    def resumo_executivo(self):
        return {
            "plano_id": self.plano_id,
            "versao": self.versao,

            "resultado_preliminar": (
                self.resultado_preliminar
            ),

            "quantidade_itens": (
                self.quantidade_itens
            ),

            "itens_criticos": (
                self.quantidade_itens_criticos
            ),

            "itens_com_alerta": (
                self.quantidade_itens_com_alerta
            ),

            "pendencias_criticas": len(
                self.criticos
            ),

            "alertas": len(
                self.alertas
            ),

            "valor_previsto": (
                self.valor_previsto
            ),

            "valor_executado": (
                self.valor_executado
            ),

            "saldo": (
                self.saldo
            ),

            "percentual_execucao": (
                self.percentual_execucao
            ),

            "conclusao_executiva": (
                self.conclusao_executiva
            ),
        }


def gerar_conclusao_executiva_plano(
    resultado,
):
    if resultado.criticos:
        return (
            "A análise consolidada do Plano de Trabalho "
            "identificou pendências críticas em um ou mais "
            "itens da execução. "
            f"Foram analisados "
            f"{resultado.quantidade_itens} item(ns), "
            f"dos quais "
            f"{resultado.quantidade_itens_criticos} "
            "apresentam pendência crítica. "
            f"Valor total previsto: R$ "
            f"{resultado.valor_previsto}; "
            f"valor executado: R$ "
            f"{resultado.valor_executado}; "
            f"saldo: R$ {resultado.saldo}. "
            "Recomenda-se análise técnica e documental "
            "dos itens críticos antes da conclusão da "
            "prestação de contas. "
            "Esta consolidação não aplica glosa "
            "automaticamente."
        )

    if resultado.alertas:
        return (
            "A análise consolidada do Plano de Trabalho "
            "não identificou pendência crítica, porém "
            "existem pontos que requerem conferência "
            "técnica ou documental. "
            f"Foram analisados "
            f"{resultado.quantidade_itens} item(ns), "
            f"com {resultado.quantidade_itens_com_alerta} "
            "item(ns) contendo alerta(s). "
            f"Valor total previsto: R$ "
            f"{resultado.valor_previsto}; "
            f"valor executado: R$ "
            f"{resultado.valor_executado}; "
            f"saldo: R$ {resultado.saldo}. "
            "A conclusão definitiva deve considerar "
            "documentos, justificativas, alterações do "
            "Plano e demais normas aplicáveis."
        )

    return (
        "Não foram identificadas inconsistências "
        "relevantes nas verificações automáticas dos "
        "itens ativos do Plano de Trabalho. "
        f"Foram analisados "
        f"{resultado.quantidade_itens} item(ns). "
        f"Valor total previsto: R$ "
        f"{resultado.valor_previsto}; "
        f"valor executado: R$ "
        f"{resultado.valor_executado}; "
        f"saldo: R$ {resultado.saldo}. "
        "A ausência de achados automáticos não substitui "
        "a conferência documental, material e normativa "
        "da prestação de contas."
    )


def analisar_plano_trabalho_completo(
    plano,
    contexto=None,
):
    itens = (
        ItemPlanoTrabalho.objects
        .filter(
            plano=plano,
            ativo=True,
        )
        .select_related(
            "plano",
            "plano__termo",
            "meta",
            "meta__prestacao",
        )
        .order_by(
            "codigo",
            "pk",
        )
    )

    resultados_itens = []

    valor_previsto = Decimal("0.00")
    valor_executado = Decimal("0.00")

    todos_achados = []

    for item in itens:
        resultado_item = (
            analisar_item_plano_completo(
                item,
                contexto=contexto,
            )
        )

        resultados_itens.append(
            resultado_item
        )

        financeiro = (
            resultado_item
            .financeiro
            .resumo
        )

        valor_previsto += (
            financeiro.valor_previsto
        )

        valor_executado += (
            financeiro.valor_executado
        )

        todos_achados.extend(
            resultado_item.achados
        )

    valor_previsto = (
        valor_previsto.quantize(
            Decimal("0.01")
        )
    )

    valor_executado = (
        valor_executado.quantize(
            Decimal("0.01")
        )
    )

    saldo = (
        valor_previsto
        - valor_executado
    ).quantize(
        Decimal("0.01")
    )

    achados = _ordenar_achados(
        _deduplicar_achados(
            todos_achados
        )
    )

    resultado = (
        ResultadoConsolidadoPlanoTrabalho(
            plano_id=plano.pk,
            versao=plano.versao,
            itens=resultados_itens,
            achados=achados,
            valor_previsto=valor_previsto,
            valor_executado=valor_executado,
            saldo=saldo,
        )
    )

    resultado.conclusao_executiva = (
        gerar_conclusao_executiva_plano(
            resultado
        )
    )

    return resultado
