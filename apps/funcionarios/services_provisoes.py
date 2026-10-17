from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Q

from .models import (
    ParametroTrabalhista,
    ProvisaoTrabalhista,
)


CENTAVOS = Decimal("0.01")


def moeda(valor):
    return Decimal(valor).quantize(
        CENTAVOS,
        rounding=ROUND_HALF_UP,
    )


def parametro_trabalhista_vigente(
    codigo,
    data_referencia,
):
    """
    Retorna o parâmetro legal/corporativo
    vigente na data informada.

    Nenhum percentual ? embutido no código.
    """

    return (
        ParametroTrabalhista.objects
        .filter(
            codigo=codigo,
            ativo=True,
            vigencia_inicio__lte=data_referencia,
        )
        .filter(
            Q(vigencia_fim__isnull=True)
            | Q(
                vigencia_fim__gte=data_referencia
            )
        )
        .order_by(
            "-vigencia_inicio",
            "-pk",
        )
        .first()
    )


def calcular_por_percentual(
    base_calculo,
    percentual,
):
    """
    percentual=8 significa 8%.
    """

    base = Decimal(base_calculo)
    taxa = Decimal(percentual)

    return moeda(
        base
        * taxa
        / Decimal("100")
    )


def criar_ou_atualizar_provisao(
    *,
    funcionario,
    competencia,
    tipo,
    base_calculo,
    valor,
    vinculo_parceria=None,
    percentual=None,
    quantidade_avos=None,
    parametro=None,
    fundamento="",
    memoria_calculo="",
    origem="automatica",
):
    """
    Ledger mensal auditável.

    Uma nova execução automática da mesma
    competência/tipo atualiza a provisão
    automática existente, sem duplicá-la.
    """

    filtros = {
        "funcionario": funcionario,
        "competencia": competencia,
        "tipo": tipo,
        "origem": origem,
        "vinculo_parceria": vinculo_parceria,
    }

    defaults = {
        "base_calculo": moeda(
            base_calculo
        ),
        "valor": moeda(
            valor
        ),
        "percentual": percentual,
        "quantidade_avos": quantidade_avos,
        "parametro": parametro,
        "fundamento": fundamento,
        "memoria_calculo": memoria_calculo,
    }

    obj, criada = (
        ProvisaoTrabalhista.objects
        .update_or_create(
            defaults=defaults,
            **filtros,
        )
    )

    return obj, criada
