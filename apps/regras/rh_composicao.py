from dataclasses import dataclass, field
from decimal import Decimal

from apps.documentos.models import Documento
from apps.lancamentos.models import Lancamento
from apps.regras.context import ContextoRegras
from apps.regras.resultado import ResultadoRegra
from apps.regras.rules.rh_composicao import (
    calcular_composicao_despesa_rh,
)


def _d(valor):
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01")
    )


@dataclass
class ResultadoComposicaoRH:
    folha_pagamento_id: int
    funcionario_id: int
    competencia: object
    composicao: object
    valor_lancado: Decimal
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
    def diferenca_lancado_e_potencial(self):
        return _d(
            self.valor_lancado
            - self.composicao.valor_potencialmente_elegivel
        )

    @property
    def resultado_preliminar(self):
        if self.criticos:
            return "pendencia_critica"

        if self.alertas:
            return "requer_conferencia"

        return "composicao_sem_inconsistencia_detectada"


def analisar_composicao_rh(folha, contexto=None):
    contexto = contexto or ContextoRegras()

    composicao = calcular_composicao_despesa_rh(
        folha
    )

    funcionario = folha.funcionario
    competencia = folha.competencia

    documentos = Documento.objects.filter(
        pertence=funcionario,
        lancamento__isnull=False,
    )

    lancamento_ids = documentos.values_list(
        "lancamento_id",
        flat=True,
    ).distinct()

    lancamentos = Lancamento.objects.filter(
        pk__in=lancamento_ids,
        data_documento__year=competencia.year,
        data_documento__month=competencia.month,
    )

    valor_lancado = _d(
        sum(
            (
                lancamento.valor_documento
                for lancamento in lancamentos
            ),
            Decimal("0.00"),
        )
    )

    achados = []

    # ---------------------------------------------------------
    # Valor lançado superior ao potencialmente elegível
    # ---------------------------------------------------------
    if (
        valor_lancado > 0
        and valor_lancado
        > composicao.valor_potencialmente_elegivel
    ):
        diferenca = _d(
            valor_lancado
            - composicao.valor_potencialmente_elegivel
        )

        achados.append(
            ResultadoRegra(
                codigo="RH_VALOR_LANCADO_SUPERIOR_POTENCIAL",
                severidade="critico",
                titulo="Valor lançado superior à composição potencial de RH",
                descricao=(
                    "O total dos lançamentos relacionados à folha supera "
                    "o valor potencialmente elegível calculado com base "
                    "nos dados atualmente disponíveis."
                ),
                regra="RH_VALOR_LANCADO_SUPERIOR_POTENCIAL",
                categoria="composicao_rh",
                resultado="achado",
                fato_verificado=(
                    "Valor lançado superior à referência calculada."
                ),
                evidencia=(
                    f"valor_lancado={valor_lancado}; "
                    f"valor_potencial={composicao.valor_potencialmente_elegivel}; "
                    f"diferenca={diferenca}."
                ),
                risco_glosa=(
                    "Elevado quanto à parcela excedente caso não exista "
                    "composição adicional prevista, comprovada e elegível."
                ),
                recomendacao=(
                    "Conferir folha, memória de cálculo, encargos, verbas "
                    "trabalhistas, rateios, Plano de Trabalho e documentos "
                    "antes de qualquer decisão sobre eventual glosa."
                ),
            )
        )

    # ---------------------------------------------------------
    # Valor lançado inferior à composição
    # ---------------------------------------------------------
    elif (
        valor_lancado > 0
        and valor_lancado
        < composicao.valor_potencialmente_elegivel
    ):
        diferenca = _d(
            composicao.valor_potencialmente_elegivel
            - valor_lancado
        )

        achados.append(
            ResultadoRegra(
                codigo="RH_VALOR_LANCADO_INFERIOR_POTENCIAL",
                severidade="info",
                titulo="Valor lançado inferior à composição potencial de RH",
                descricao=(
                    "O total lançado é inferior ao valor potencialmente "
                    "elegível identificado na composição da folha."
                ),
                regra="RH_VALOR_LANCADO_INFERIOR_POTENCIAL",
                categoria="composicao_rh",
                resultado="informativo",
                fato_verificado=(
                    "Valor lançado inferior à referência calculada."
                ),
                evidencia=(
                    f"valor_lancado={valor_lancado}; "
                    f"valor_potencial={composicao.valor_potencialmente_elegivel}; "
                    f"diferenca={diferenca}."
                ),
                risco_glosa="",
                recomendacao=(
                    "Conferir se parte da despesa foi custeada com recursos "
                    "próprios, rateada, registrada em outro lançamento ou "
                    "não apresentada à parceria."
                ),
            )
        )

    # ---------------------------------------------------------
    # Faltas/atrasos
    # ---------------------------------------------------------
    if composicao.faltas_atrasos > 0:
        achados.append(
            ResultadoRegra(
                codigo="RH_COMPOSICAO_CONTEM_DESCONTO_FALTAS",
                severidade="info",
                titulo="Composição considera faltas ou atrasos",
                descricao=(
                    "A composição potencial da despesa foi reduzida pelo "
                    "valor calculado de faltas e atrasos."
                ),
                regra="RH_COMPOSICAO_CONTEM_DESCONTO_FALTAS",
                categoria="composicao_rh",
                resultado="informativo",
                fato_verificado=(
                    "Existe desconto financeiro decorrente de faltas/atrasos."
                ),
                evidencia=(
                    f"desconto_faltas={composicao.faltas_atrasos}."
                ),
                risco_glosa="",
                recomendacao=(
                    "Confirmar folha de ponto, justificativas e eventual "
                    "abono antes de consolidar o valor elegível."
                ),
            )
        )

    # ---------------------------------------------------------
    # Verbas rescisórias
    # ---------------------------------------------------------
    if composicao.verbas_rescisorias_identificadas > 0:
        achados.append(
            ResultadoRegra(
                codigo="RH_COMPOSICAO_VERBAS_RESCISORIAS",
                severidade="alerta",
                titulo="Composição contém verbas rescisórias",
                descricao=(
                    "Foram identificados valores rescisórios ou proporcionais "
                    "na composição da despesa de RH."
                ),
                regra="RH_COMPOSICAO_VERBAS_RESCISORIAS",
                categoria="composicao_rh",
                resultado="nao_verificado",
                fato_verificado=(
                    "Existem verbas rescisórias/proporcionais cadastradas."
                ),
                evidencia=(
                    f"total_rescisorio_identificado="
                    f"{composicao.verbas_rescisorias_identificadas}."
                ),
                risco_glosa=(
                    "Indeterminado até verificar natureza, competência, "
                    "período aquisitivo, vínculo com a parceria e "
                    "documentação rescisória."
                ),
                recomendacao=(
                    "Conferir TRCT, aviso-prévio, férias, 1/3, 13º, FGTS, "
                    "período trabalhado e critérios do Plano de Trabalho."
                ),
            )
        )

    return ResultadoComposicaoRH(
        folha_pagamento_id=folha.pk,
        funcionario_id=funcionario.pk,
        competencia=competencia,
        composicao=composicao,
        valor_lancado=valor_lancado,
        achados=achados,
    )
