from django.core.exceptions import ValidationError

from apps.pareceres.models import (
    HistoricoParecer,
    ItemParecer,
    ParecerTecnico,
)


def _texto(valor):
    return str(valor or "").strip()


def _validar_usuario(usuario):
    if usuario is None or not getattr(usuario, "pk", None):
        raise ValidationError(
            "O registro de auditoria exige usuário identificado."
        )


def registrar_historico(
    *,
    parecer,
    acao,
    usuario,
    situacao_anterior="",
    nova_situacao="",
    conclusao_anterior="",
    nova_conclusao="",
    observacao="",
):
    """
    Registra evento imutável na trilha do parecer.

    Não altera o parecer, item, diligência, glosa
    ou prestação de contas.
    """

    if not isinstance(parecer, ParecerTecnico):
        raise ValidationError(
            "O parecer informado é inválido."
        )

    if not parecer.pk:
        raise ValidationError(
            "O parecer deve estar salvo."
        )

    _validar_usuario(usuario)

    acao = _texto(acao)

    if not acao:
        raise ValidationError(
            "A ação de auditoria deve ser informada."
        )

    historico = HistoricoParecer(
        parecer=parecer,
        acao=acao[:100],
        situacao_anterior=_texto(
            situacao_anterior
        ),
        nova_situacao=_texto(
            nova_situacao
        ),
        conclusao_anterior=_texto(
            conclusao_anterior
        ),
        nova_conclusao=_texto(
            nova_conclusao
        ),
        observacao=_texto(
            observacao
        ),
        usuario=usuario,
    )

    historico.full_clean()
    historico.save()

    return historico



def registrar_aprovacao_parecer(
    *,
    parecer,
    usuario,
    situacao_anterior,
    conclusao_anterior,
):
    """
    Registra a aprovação humana e o fechamento do parecer.

    A função apenas registra a auditoria. A alteração do
    ParecerTecnico é responsabilidade da camada de serviço/view.
    """

    return registrar_historico(
        parecer=parecer,
        acao="PARECER_APROVADO",
        usuario=usuario,
        situacao_anterior=situacao_anterior,
        nova_situacao=parecer.situacao,
        conclusao_anterior=conclusao_anterior,
        nova_conclusao=parecer.tipo_conclusao,
        observacao=(
            "Parecer aprovado por decisão humana e finalizado."
        ),
    )


def registrar_revisao_parecer(
    *,
    parecer,
    usuario,
    situacao_anterior,
    conclusao_anterior,
):
    return registrar_historico(
        parecer=parecer,
        acao="REVISAO_PARECER",
        usuario=usuario,
        situacao_anterior=situacao_anterior,
        nova_situacao=parecer.situacao,
        conclusao_anterior=conclusao_anterior,
        nova_conclusao=parecer.tipo_conclusao,
        observacao=(
            "Revisão humana do parecer registrada."
        ),
    )


def registrar_revisao_item(
    *,
    item,
    usuario,
    conclusao_anterior,
):
    if not isinstance(item, ItemParecer):
        raise ValidationError(
            "O item informado é inválido."
        )

    identificador = (
        item.codigo
        or item.codigo_regra
        or str(item.pk)
    )

    return registrar_historico(
        parecer=item.parecer,
        acao="REVISAO_ITEM",
        usuario=usuario,
        conclusao_anterior=conclusao_anterior,
        nova_conclusao=item.conclusao_item,
        observacao=(
            f"Item {identificador} revisado pelo analista. "
            f"Manifestação: "
            f"{_texto(item.manifestacao_analista) or 'não informada'}"
        ),
    )


def registrar_diligencia_criada(
    *,
    item,
    diligencia,
    usuario,
):
    identificador = (
        item.codigo
        or item.codigo_regra
        or str(item.pk)
    )

    return registrar_historico(
        parecer=item.parecer,
        acao="DILIGENCIA_CRIADA",
        usuario=usuario,
        observacao=(
            f"Diligência #{diligencia.pk} criada a partir "
            f"do item {identificador}. "
            f"Status inicial: {diligencia.status}."
        ),
    )


def registrar_reanalise_iniciada(
    *,
    item,
    diligencia,
    usuario,
    status_anterior,
):
    return registrar_historico(
        parecer=item.parecer,
        acao="REANALISE_INICIADA",
        usuario=usuario,
        observacao=(
            f"Diligência #{diligencia.pk}: "
            f"{status_anterior} -> {diligencia.status}."
        ),
    )


def registrar_saneamento(
    *,
    item,
    diligencia,
    usuario,
    conclusao_anterior,
    status_anterior,
):
    if item.conclusao_item == ItemParecer.ConclusaoItem.SANADO:
        acao = "ITEM_SANADO"
    else:
        acao = "ITEM_NAO_SANADO"

    return registrar_historico(
        parecer=item.parecer,
        acao=acao,
        usuario=usuario,
        conclusao_anterior=conclusao_anterior,
        nova_conclusao=item.conclusao_item,
        observacao=(
            f"Diligência #{diligencia.pk}: "
            f"{status_anterior} -> {diligencia.status}. "
            f"Manifestação do analista: "
            f"{_texto(item.manifestacao_analista)}"
        ),
    )
