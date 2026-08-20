from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.diligencias.models import Diligencia
from apps.pareceres.auditoria import (
    registrar_reanalise_iniciada,
    registrar_saneamento,
)
from apps.pareceres.models import ItemParecer


DECISAO_SANADO = "SANADO"
DECISAO_NAO_SANADO = "NAO_SANADO"


def _validar_item_com_diligencia(item):
    if not isinstance(item, ItemParecer):
        raise ValidationError(
            "O item informado nao e um ItemParecer valido."
        )

    if not item.pk:
        raise ValidationError(
            "O ItemParecer deve estar salvo."
        )

    if not item.diligencia_id:
        raise ValidationError(
            "O item do parecer nao possui diligencia vinculada."
        )

    return item.diligencia


def _validar_usuario(usuario):
    if usuario is None or not getattr(usuario, "pk", None):
        raise ValidationError(
            "A operacao exige usuario responsavel."
        )


def _exigir_resposta(diligencia):
    if not diligencia.respostas.exists():
        raise ValidationError(
            "A diligencia ainda nao possui resposta registrada."
        )


@transaction.atomic
def iniciar_reanalise_diligencia(
    *,
    item,
    usuario,
):
    """
    Coloca a diligencia em reanalise apos resposta da OSC.

    Esta operacao NAO conclui automaticamente que:
    - a pendencia foi sanada;
    - houve irregularidade;
    - deve existir glosa;
    - o parecer deve ser finalizado.
    """

    _validar_usuario(usuario)

    diligencia = _validar_item_com_diligencia(
        item
    )

    _exigir_resposta(diligencia)

    if diligencia.status in {
        Diligencia.Status.ATENDIDA,
        Diligencia.Status.NAO_ATENDIDA,
        Diligencia.Status.CANCELADA,
    }:
        raise ValidationError(
            "A diligencia ja esta encerrada ou cancelada."
        )

    status_anterior = diligencia.status

    diligencia.status = Diligencia.Status.REANALISE

    diligencia.save(
        update_fields=[
            "status",
            "atualizado_em",
        ]
    )

    registrar_reanalise_iniciada(
        item=item,
        diligencia=diligencia,
        usuario=usuario,
        status_anterior=status_anterior,
    )

    return diligencia


@transaction.atomic
def concluir_reanalise_diligencia(
    *,
    item,
    usuario,
    decisao,
    manifestacao,
):
    """
    Registra a conclusao HUMANA da reanalise.

    decisoes permitidas:
    - SANADO
    - NAO_SANADO

    A funcao nao registra glosa e nao altera
    automaticamente a conclusao global do parecer.
    """

    _validar_usuario(usuario)

    diligencia = _validar_item_com_diligencia(
        item
    )

    _exigir_resposta(diligencia)

    decisao = str(
        decisao or ""
    ).strip().upper()

    manifestacao = str(
        manifestacao or ""
    ).strip()

    if decisao not in {
        DECISAO_SANADO,
        DECISAO_NAO_SANADO,
    }:
        raise ValidationError(
            "Decisao de saneamento invalida."
        )

    if not manifestacao:
        raise ValidationError(
            "A conclusao da reanalise exige manifestacao do analista."
        )

    if diligencia.status != Diligencia.Status.REANALISE:
        raise ValidationError(
            "A diligencia deve estar em reanalise antes da conclusao."
        )

    conclusao_anterior = item.conclusao_item
    status_anterior = diligencia.status

    if decisao == DECISAO_SANADO:
        item.conclusao_item = (
            ItemParecer.ConclusaoItem.SANADO
        )
        diligencia.status = (
            Diligencia.Status.ATENDIDA
        )
    else:
        item.conclusao_item = (
            ItemParecer.ConclusaoItem.NAO_SANADO
        )
        diligencia.status = (
            Diligencia.Status.NAO_ATENDIDA
        )

    item.manifestacao_analista = manifestacao

    item.full_clean()

    item.save(
        update_fields=[
            "conclusao_item",
            "manifestacao_analista",
            "atualizado_em",
        ]
    )

    diligencia.encerrada_em = timezone.now()

    diligencia.save(
        update_fields=[
            "status",
            "encerrada_em",
            "atualizado_em",
        ]
    )

    registrar_saneamento(
        item=item,
        diligencia=diligencia,
        usuario=usuario,
        conclusao_anterior=conclusao_anterior,
        status_anterior=status_anterior,
    )

    return item
