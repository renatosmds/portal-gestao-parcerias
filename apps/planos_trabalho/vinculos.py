from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    PlanoTrabalho,
    VinculoLancamentoItemPlano,
)
from .services import plano_aplicavel_em


def data_referencia_lancamento(lancamento):
    """
    Referência técnica inicial para selecionar a versão
    histórica do Plano.

    Prioridade:
    1. data do documento;
    2. data do pagamento.

    A escolha não substitui análise jurídica específica
    sobre competência ou elegibilidade da despesa.
    """

    return (
        getattr(
            lancamento,
            "data_documento",
            None,
        )
        or getattr(
            lancamento,
            "data_pagamento",
            None,
        )
    )


def validar_item_para_lancamento(
    lancamento,
    item_plano,
):
    erros = {}

    termo = getattr(
        lancamento,
        "termo",
        None,
    )

    if not termo:
        erros["lancamento"] = (
            "O lançamento não possui Termo associado."
        )

    elif (
        item_plano.plano.termo_id
        != termo.pk
    ):
        erros["item_plano"] = (
            "O item selecionado pertence a outro Termo."
        )

    data_referencia = (
        data_referencia_lancamento(
            lancamento
        )
    )

    if not data_referencia:
        erros["data_referencia"] = (
            "Não foi possível determinar a data de "
            "referência do lançamento."
        )

    if erros:
        raise ValidationError(erros)

    plano_aplicavel = plano_aplicavel_em(
        termo,
        data_referencia,
    )

    if not plano_aplicavel:
        raise ValidationError(
            {
                "plano": (
                    "Não foi localizada versão do Plano "
                    "aplicável à data do lançamento."
                )
            }
        )

    if (
        item_plano.plano_id
        != plano_aplicavel.pk
    ):
        raise ValidationError(
            {
                "item_plano": (
                    "O item pertence a uma versão do Plano "
                    "diferente daquela aplicável à data "
                    "do lançamento."
                )
            }
        )

    if not item_plano.ativo:
        raise ValidationError(
            {
                "item_plano": (
                    "O item do Plano está inativo."
                )
            }
        )

    return plano_aplicavel


@transaction.atomic
def vincular_lancamento_item(
    lancamento,
    item_plano,
    *,
    origem=(
        VinculoLancamentoItemPlano
        .OrigemVinculo
        .MANUAL
    ),
    confianca=None,
    justificativa="",
    quantidade_executada=None,
    valor_unitario_executado=None,
    unidade_executada="",
):
    """
    Cria novo vínculo preservando histórico.

    Caso exista vínculo ativo anterior, ele é
    desativado antes da criação do novo.
    """

    validar_item_para_lancamento(
        lancamento,
        item_plano,
    )

    VinculoLancamentoItemPlano.objects.filter(
        lancamento=lancamento,
        ativo=True,
    ).update(
        ativo=False
    )

    vinculo = VinculoLancamentoItemPlano(
        lancamento=lancamento,
        item_plano=item_plano,
        origem=origem,
        confianca=confianca,
        justificativa=justificativa,
        quantidade_executada=quantidade_executada,
        valor_unitario_executado=valor_unitario_executado,
        unidade_executada=unidade_executada,
        ativo=True,
    )

    vinculo.full_clean()
    vinculo.save()

    return vinculo


def vinculo_ativo_lancamento(lancamento):
    return (
        VinculoLancamentoItemPlano.objects
        .filter(
            lancamento=lancamento,
            ativo=True,
        )
        .select_related(
            "item_plano",
            "item_plano__plano",
        )
        .first()
    )

