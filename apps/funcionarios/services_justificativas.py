from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    DecisaoJustificativa,
    JustificativaPonto,
)


ZERO_HORAS = Decimal("0.00")


def horas_de_minutos(minutos):
    """
    Converte minutos exatos da camada de decisão
    para horas decimais usadas pelo motor legado.
    """
    return (
        Decimal(minutos)
        / Decimal("60")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def criar_justificativa(
    *,
    funcionario,
    dia_folha_ponto,
    tipo,
    ocorrencia,
    motivo,
    minutos_solicitados,
    inicio=None,
    fim=None,
    referencia_documento="",
    solicitado_por=None,
):
    """
    Cria solicitação ainda sem presumir deferimento.
    """

    justificativa = JustificativaPonto(
        funcionario=funcionario,
        dia_folha_ponto=dia_folha_ponto,
        tipo=tipo,
        ocorrencia=ocorrencia,
        motivo=motivo,
        inicio=inicio,
        fim=fim,
        minutos_solicitados=minutos_solicitados,
        referencia_documento=(
            referencia_documento
            or ""
        ),
        solicitado_por=solicitado_por,
    )

    justificativa.full_clean()
    justificativa.save()

    return justificativa


def _snapshot_tipo(tipo):
    """
    Snapshot auditável da regra utilizada.
    """

    return {
        "tipo_id": tipo.pk,
        "codigo": tipo.codigo,
        "nome": tipo.nome,
        "fundamento_tipo": (
            tipo.fundamento_tipo
        ),
        "fundamento": tipo.fundamento,
        "dispositivo": tipo.dispositivo,
        "fonte": tipo.fonte,
        "vigencia_inicio": (
            tipo.vigencia_inicio.isoformat()
        ),
        "vigencia_fim": (
            tipo.vigencia_fim.isoformat()
            if tipo.vigencia_fim
            else None
        ),
        "exige_documento": (
            tipo.exige_documento
        ),
        "documento_sensivel": (
            tipo.documento_sensivel
        ),
        "permite_abono_parcial": (
            tipo.permite_abono_parcial
        ),
        "permite_compensacao": (
            tipo.permite_compensacao
        ),
    }


@transaction.atomic
def registrar_decisao(
    *,
    justificativa,
    decisao,
    decidido_por,
    fundamento_tipo,
    fundamento,
    motivacao,
    minutos_abonados=None,
    minutos_compensar=0,
    dispositivo="",
    fonte="",
):
    """
    Registra decisão append-only.

    Uma nova decisão desativa a anterior, mantendo
    a decisão substituída para auditoria.
    """

    justificativa = (
        JustificativaPonto.objects
        .select_for_update()
        .select_related(
            "tipo",
            "dia_folha_ponto",
        )
        .get(
            pk=justificativa.pk
        )
    )

    anterior = (
        DecisaoJustificativa.objects
        .select_for_update()
        .filter(
            justificativa=justificativa,
            ativo=True,
        )
        .order_by(
            "-decidido_em",
            "-pk",
        )
        .first()
    )

    if anterior:

        DecisaoJustificativa.objects.filter(
            pk=anterior.pk
        ).update(
            ativo=False
        )

    if (
        decisao == "abono_integral"
        and minutos_abonados is None
    ):

        minutos_abonados = (
            justificativa
            .minutos_solicitados
        )

    minutos_abonados = (
        minutos_abonados
        if minutos_abonados is not None
        else 0
    )

    objeto = DecisaoJustificativa(
        justificativa=justificativa,
        decisao=decisao,
        minutos_abonados=(
            minutos_abonados
        ),
        minutos_compensar=(
            minutos_compensar
        ),
        fundamento_tipo=(
            fundamento_tipo
        ),
        fundamento=fundamento,
        dispositivo=(
            dispositivo
            or ""
        ),
        fonte=(
            fonte
            or ""
        ),
        motivacao=motivacao,
        snapshot_regra=(
            _snapshot_tipo(
                justificativa.tipo
            )
        ),
        decidido_por=decidido_por,
        substitui=anterior,
        ativo=True,
    )

    objeto.full_clean()
    objeto.save()

    status_por_decisao = {
        "abono_integral": "deferida",
        "abono_parcial": (
            "deferida_parcial"
        ),
        "indeferido": "indeferida",
        "compensacao": "compensacao",
    }

    justificativa.status = (
        status_por_decisao[
            decisao
        ]
    )

    justificativa.save(
        update_fields=[
            "status",
            "atualizado_em",
        ]
    )

    return objeto


def decisoes_ativas_dia(
    dia_folha_ponto,
):
    """
    Retorna somente decisões vigentes/ativas
    vinculadas ao dia.
    """

    return (
        DecisaoJustificativa.objects
        .filter(
            justificativa__dia_folha_ponto=(
                dia_folha_ponto
            ),
            ativo=True,
        )
        .select_related(
            "justificativa",
            "justificativa__tipo",
        )
        .order_by(
            "pk"
        )
    )


def resumo_decisoes_dia(
    dia_folha_ponto,
):
    """
    Soma efeitos das decisões ativas do dia.

    Os valores permanecem em minutos nesta camada.
    """

    abonados = 0
    compensar = 0
    ids = []

    for decisao in decisoes_ativas_dia(
        dia_folha_ponto
    ):

        abonados += (
            decisao.minutos_abonados
        )

        compensar += (
            decisao.minutos_compensar
        )

        ids.append(
            decisao.pk
        )

    return {
        "minutos_abonados": abonados,
        "minutos_compensar": compensar,
        "decisoes": ids,
    }


def aplicar_decisoes_justificativas_apuracao(
    dia,
    resultado,
):
    """
    Aplica os efeitos das decisoes ativas ao dia.

    Regras:
    - abono reduz deficit;
    - compensacao nao e abono;
    - compensacao autoriza somente a parcela expressa;
    - marcacoes nunca sao inventadas;
    - falta integral pode ser regularizada por decisao
      expressa de abono ou compensacao;
    - reprocessamento e idempotente.
    """

    resumo = resumo_decisoes_dia(
        dia
    )

    minutos_abonados = resumo[
        "minutos_abonados"
    ]

    minutos_compensar = resumo[
        "minutos_compensar"
    ]

    resultado[
        "decisoes_justificativas"
    ] = resumo[
        "decisoes"
    ]

    resultado[
        "minutos_compensacao_autorizada"
    ] = minutos_compensar

    # Somente dias normais de trabalho recebem
    # efeitos desta camada.
    if dia.tipo_dia != "trabalho":

        resultado[
            "horas_compensacao_autorizada"
        ] = ZERO_HORAS

        return resultado

    previstas = (
        dia.horas_previstas
        or ZERO_HORAS
    )

    horas_abono = horas_de_minutos(
        minutos_abonados
    )

    horas_compensacao = (
        horas_de_minutos(
            minutos_compensar
        )
    )

    resultado[
        "horas_abonadas"
    ] = ZERO_HORAS

    resultado[
        "horas_compensacao_autorizada"
    ] = ZERO_HORAS

    # -----------------------------------------------------
    # AUSENCIA TOTAL SEM MARCACOES
    # -----------------------------------------------------

    if (
        resultado.get("status")
        == "sem_marcacao"
    ):

        if previstas <= ZERO_HORAS:

            return resultado

        abono = min(
            horas_abono,
            previstas,
        )

        resultado[
            "horas_abonadas"
        ] = abono

        restante = (
            previstas
            - abono
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        if restante <= ZERO_HORAS:

            resultado[
                "status"
            ] = "falta_integral_abonada"

            resultado[
                "horas_faltas_atrasos"
            ] = ZERO_HORAS

            resultado[
                "saldo_banco_candidato"
            ] = ZERO_HORAS

            resultado[
                "mensagem"
            ] = (
                "Ausencia integral coberta por "
                "decisao de abono."
            )

            return resultado

        compensacao = min(
            horas_compensacao,
            restante,
        )

        resultado[
            "horas_compensacao_autorizada"
        ] = compensacao

        # So uma decisao que cubra todo o restante
        # permite liberar uma ausencia total sem marcacoes.
        if compensacao >= restante:

            resultado[
                "status"
            ] = (
                "falta_integral_"
                "compensacao_autorizada"
            )

            resultado[
                "horas_faltas_atrasos"
            ] = restante

            resultado[
                "saldo_banco_candidato"
            ] = -restante

            resultado[
                "mensagem"
            ] = (
                "Ausencia integral formalmente "
                "autorizada para compensacao."
            )

        else:

            resultado[
                "mensagem"
            ] = (
                "A regularizacao parcial nao cobre "
                "integralmente o dia sem marcacoes."
            )

        return resultado

    # -----------------------------------------------------
    # JORNADA COM MARCACOES E DEFICIT
    # -----------------------------------------------------

    deficit_original = (
        resultado.get(
            "horas_faltas_atrasos",
            ZERO_HORAS,
        )
        or ZERO_HORAS
    )

    if deficit_original <= ZERO_HORAS:

        return resultado

    abono = min(
        deficit_original,
        horas_abono,
    )

    deficit_pos_abono = (
        deficit_original
        - abono
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    compensacao = min(
        deficit_pos_abono,
        horas_compensacao,
    )

    resultado[
        "horas_abonadas"
    ] = abono

    resultado[
        "horas_compensacao_autorizada"
    ] = compensacao

    resultado[
        "horas_faltas_atrasos"
    ] = deficit_pos_abono

    resultado[
        "saldo_banco_candidato"
    ] = (
        -deficit_pos_abono
        if deficit_pos_abono > ZERO_HORAS
        else ZERO_HORAS
    )

    if deficit_pos_abono == ZERO_HORAS:

        resultado[
            "status"
        ] = "jornada_justificada"

        resultado[
            "mensagem"
        ] = (
            "Deficit integralmente coberto por abono."
        )

    elif compensacao >= deficit_pos_abono:

        resultado[
            "status"
        ] = "jornada_compensacao_autorizada"

        resultado[
            "mensagem"
        ] = (
            "Deficit remanescente integralmente "
            "autorizado para compensacao."
        )

    elif compensacao > ZERO_HORAS:

        resultado[
            "status"
        ] = (
            "jornada_compensacao_parcial"
        )

        resultado[
            "mensagem"
        ] = (
            "Parte do deficit foi autorizada para "
            "compensacao; o restante permanece "
            "para tratamento em folha."
        )

    elif abono > ZERO_HORAS:

        resultado[
            "status"
        ] = (
            "jornada_incompleta_"
            "justificada_parcial"
        )

        resultado[
            "mensagem"
        ] = (
            "Deficit parcialmente coberto por abono."
        )

    return resultado
