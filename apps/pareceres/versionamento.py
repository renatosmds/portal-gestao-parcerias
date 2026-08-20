from copy import deepcopy

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.pareceres.auditoria import registrar_historico
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)


def _copiar_relacionados_item(item_origem, item_destino, related_name):
    """
    Copia registros estruturados pertencentes ao item.

    ForeignKeys para objetos externos são preservadas;
    os objetos externos não são duplicados.
    """

    manager = getattr(
        item_origem,
        related_name,
        None,
    )

    if manager is None:
        return

    for origem in manager.all():

        modelo = origem.__class__
        dados = {}

        for campo in modelo._meta.concrete_fields:

            if campo.primary_key:
                continue

            if campo.name == "item":
                continue

            if getattr(campo, "auto_now", False):
                continue

            if getattr(campo, "auto_now_add", False):
                continue

            valor = getattr(
                origem,
                campo.attname,
            )

            if not campo.is_relation:
                valor = deepcopy(valor)

            dados[campo.attname] = valor

        novo = modelo(
            item=item_destino,
            **dados,
        )

        novo.full_clean()
        novo.save()


def _copiar_item(
    *,
    item,
    novo_parecer,
    usuario,
):
    novo = ItemParecer(
        parecer=novo_parecer,
        codigo=item.codigo,
        codigo_regra=item.codigo_regra,
        categoria=item.categoria,
        severidade=item.severidade,
        origem=item.origem,
        titulo=item.titulo,
        descricao=item.descricao,
        fato_verificado=item.fato_verificado,
        evidencia=item.evidencia,
        fundamentacao=item.fundamentacao,
        risco_glosa=item.risco_glosa,
        recomendacao=item.recomendacao,
        manifestacao_analista=item.manifestacao_analista,
        conclusao_item=item.conclusao_item,
        resultado_origem=item.resultado_origem,
        origem_normativa=item.origem_normativa,
        dados_origem=deepcopy(
            item.dados_origem
        ),
        lancamento=item.lancamento,
        documento=item.documento,
        diligencia=item.diligencia,
        ordem=item.ordem,
        criado_por=usuario,
    )

    novo.full_clean()
    novo.save()

    _copiar_relacionados_item(
        item,
        novo,
        "evidencias_estruturadas",
    )

    _copiar_relacionados_item(
        item,
        novo,
        "fundamentacoes_estruturadas",
    )

    return novo


@transaction.atomic
def criar_nova_versao_parecer(
    *,
    parecer,
    usuario,
):
    """
    Cria nova versão editável a partir de parecer FINALIZADO.

    A versão anterior é preservada e passa a SUBSTITUIDO.
    """

    if usuario is None or not getattr(
        usuario,
        "pk",
        None,
    ):
        raise ValidationError(
            "A criação de nova versão exige usuário identificado."
        )

    parecer = (
        ParecerTecnico.objects
        .select_for_update()
        .select_related(
            "prestacao",
            "empresa",
        )
        .get(pk=parecer.pk)
    )

    if (
        parecer.situacao
        != ParecerTecnico.Situacao.FINALIZADO
    ):
        raise ValidationError(
            "Somente parecer finalizado pode originar nova versão."
        )

    if parecer.versoes_posteriores.exists():
        raise ValidationError(
            "Este parecer já possui versão posterior."
        )

    proxima_versao = parecer.versao + 1

    if ParecerTecnico.objects.filter(
        prestacao=parecer.prestacao,
        versao=proxima_versao,
    ).exists():
        raise ValidationError(
            "Já existe a próxima versão para esta prestação."
        )

    novo = ParecerTecnico(
        prestacao=parecer.prestacao,
        empresa=parecer.empresa,
        numero=parecer.numero,
        versao=proxima_versao,
        versao_anterior=parecer,
        situacao=(
            ParecerTecnico.Situacao.RASCUNHO
        ),
        tipo_conclusao=parecer.tipo_conclusao,
        resumo_executivo=parecer.resumo_executivo,
        fundamentacao_geral=parecer.fundamentacao_geral,
        conclusao=parecer.conclusao,
        ressalvas=parecer.ressalvas,
        recomendacoes_gerais=parecer.recomendacoes_gerais,
        elaborado_por=usuario,

        # Nova versão exige novo ciclo humano.
        revisado_por=None,
        revisado_em=None,
        aprovado_por=None,
        aprovado_em=None,
    )

    novo.full_clean()
    novo.save()

    for item in parecer.itens.all().order_by(
        "ordem",
        "id",
    ):
        _copiar_item(
            item=item,
            novo_parecer=novo,
            usuario=usuario,
        )

    situacao_anterior = parecer.situacao

    parecer.situacao = (
        ParecerTecnico.Situacao.SUBSTITUIDO
    )

    parecer.full_clean()

    parecer.save(
        update_fields=[
            "situacao",
            "atualizado_em",
        ]
    )

    registrar_historico(
        parecer=parecer,
        acao="PARECER_SUBSTITUIDO",
        usuario=usuario,
        situacao_anterior=situacao_anterior,
        nova_situacao=parecer.situacao,
        conclusao_anterior=parecer.tipo_conclusao,
        nova_conclusao=parecer.tipo_conclusao,
        observacao=(
            f"Parecer substituído pela versão {novo.versao} "
            f"(parecer #{novo.pk})."
        ),
    )

    registrar_historico(
        parecer=novo,
        acao="NOVA_VERSAO_CRIADA",
        usuario=usuario,
        situacao_anterior="",
        nova_situacao=novo.situacao,
        conclusao_anterior="",
        nova_conclusao=novo.tipo_conclusao,
        observacao=(
            f"Nova versão criada a partir da versão "
            f"{parecer.versao} (parecer #{parecer.pk})."
        ),
    )

    return novo
