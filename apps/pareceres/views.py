from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.pareceres.auditoria import (
    registrar_aprovacao_parecer,
    registrar_revisao_item,
    registrar_revisao_parecer,
)
from apps.pareceres.classificacao import (
    classificar_parecer_tecnicamente,
)
from apps.pareceres.conclusao_executiva import (
    gerar_conclusao_executiva,
)
from apps.pareceres.escopo import (
    itens_parecer_permitidos,
    pareceres_permitidos,
)
from apps.pareceres.forms import (
    ItemParecerRevisaoForm,
    ParecerRevisaoForm,
)
from apps.pareceres.models import ParecerTecnico
from apps.pareceres.versionamento import criar_nova_versao_parecer


def _exigir_parecer_editavel(parecer):
    permitidas = {
        ParecerTecnico.Situacao.RASCUNHO,
        ParecerTecnico.Situacao.EM_REVISAO,
    }

    if parecer.situacao not in permitidas:
        raise PermissionDenied(
            "Este parecer não está disponível para revisão."
        )



def _exigir_parecer_aprovavel(parecer):
    """
    Garante que somente um parecer efetivamente revisado
    possa ser aprovado/finalizado.
    """

    if parecer.situacao != ParecerTecnico.Situacao.EM_REVISAO:
        raise PermissionDenied(
            "Somente parecer em revisão pode ser aprovado."
        )

    if not parecer.revisado_por_id or not parecer.revisado_em:
        raise PermissionDenied(
            "O parecer deve passar por revisão humana antes da aprovação."
        )

    if parecer.aprovado_por_id or parecer.aprovado_em:
        raise PermissionDenied(
            "Este parecer já foi aprovado."
        )


def _dados_assistidos(parecer):
    classificacao = classificar_parecer_tecnicamente(
        parecer
    )

    minuta = gerar_conclusao_executiva(
        parecer
    )

    labels = dict(
        ParecerTecnico.TipoConclusao.choices
    )

    return {
        "classificacao_sugerida": classificacao,
        "classificacao_sugerida_label": labels.get(
            classificacao.classificacao_sugerida,
            classificacao.classificacao_sugerida,
        ),
        "minuta_executiva": minuta,
    }


@login_required
def parecer_lista(request):
    pareceres = pareceres_permitidos(
        request.user
    ).order_by(
        "-criado_em"
    )

    return render(
        request,
        "pareceres/parecer_lista.html",
        {
            "pareceres": pareceres,
        },
    )


@login_required
def parecer_detalhe(request, pk):
    parecer = get_object_or_404(
        pareceres_permitidos(request.user),
        pk=pk,
    )

    itens = parecer.itens.select_related(
        "diligencia",
        "documento",
        "lancamento",
    ).prefetch_related(
        "evidencias_estruturadas",
        "fundamentacoes_estruturadas",
    ).order_by(
        "ordem",
        "id",
    )

    historico = parecer.historico.select_related(
        "usuario"
    ).order_by(
        "-criado_em",
        "-id",
    )

    versao_posterior = (
        parecer.versoes_posteriores
        .order_by("versao", "id")
        .first()
    )

    contexto = {
        "parecer": parecer,
        "itens": itens,
        "historico": historico,
        "versao_posterior": versao_posterior,
    }

    contexto.update(
        _dados_assistidos(parecer)
    )

    return render(
        request,
        "pareceres/parecer_detalhe.html",
        contexto,
    )


@login_required
def parecer_revisar(request, pk):
    parecer = get_object_or_404(
        pareceres_permitidos(request.user),
        pk=pk,
    )

    _exigir_parecer_editavel(
        parecer
    )

    if request.method == "POST":
        situacao_anterior = parecer.situacao
        conclusao_anterior = parecer.tipo_conclusao

        form = ParecerRevisaoForm(
            request.POST,
            instance=parecer,
        )

        if form.is_valid():
            objeto = form.save(
                commit=False
            )

            objeto.revisado_por = request.user
            objeto.revisado_em = timezone.now()
            objeto.situacao = (
                ParecerTecnico.Situacao.EM_REVISAO
            )

            objeto.full_clean()
            objeto.save()

            registrar_revisao_parecer(
                parecer=objeto,
                usuario=request.user,
                situacao_anterior=situacao_anterior,
                conclusao_anterior=conclusao_anterior,
            )

            messages.success(
                request,
                "Revisão humana do parecer salva com sucesso.",
            )

            return redirect(
                "pareceres:parecer_detalhe",
                pk=objeto.pk,
            )
    else:
        form = ParecerRevisaoForm(
            instance=parecer
        )

    contexto = {
        "parecer": parecer,
        "form": form,
    }

    contexto.update(
        _dados_assistidos(parecer)
    )

    return render(
        request,
        "pareceres/parecer_revisao.html",
        contexto,
    )



@login_required
@require_POST
def parecer_nova_versao(request, pk):
    parecer = get_object_or_404(
        pareceres_permitidos(request.user),
        pk=pk,
    )

    try:
        novo = criar_nova_versao_parecer(
            parecer=parecer,
            usuario=request.user,
        )
    except Exception as erro:
        from django.core.exceptions import ValidationError

        if isinstance(erro, ValidationError):
            messages.error(
                request,
                " ".join(erro.messages),
            )

            return redirect(
                "pareceres:parecer_detalhe",
                pk=parecer.pk,
            )

        raise

    messages.success(
        request,
        (
            f"Versão {novo.versao} criada com sucesso. "
            "A nova versão deve passar por nova revisão "
            "e aprovação."
        ),
    )

    return redirect(
        "pareceres:parecer_detalhe",
        pk=novo.pk,
    )


@login_required
@require_POST
@transaction.atomic
def parecer_aprovar(request, pk):
    parecer = get_object_or_404(
        pareceres_permitidos(request.user),
        pk=pk,
    )

    _exigir_parecer_aprovavel(
        parecer
    )

    situacao_anterior = parecer.situacao
    conclusao_anterior = parecer.tipo_conclusao

    parecer.situacao = (
        ParecerTecnico.Situacao.FINALIZADO
    )

    parecer.aprovado_por = request.user
    parecer.aprovado_em = timezone.now()

    parecer.full_clean()

    parecer.save(
        update_fields=[
            "situacao",
            "aprovado_por",
            "aprovado_em",
            "atualizado_em",
        ]
    )

    registrar_aprovacao_parecer(
        parecer=parecer,
        usuario=request.user,
        situacao_anterior=situacao_anterior,
        conclusao_anterior=conclusao_anterior,
    )

    messages.success(
        request,
        "Parecer aprovado e finalizado com sucesso.",
    )

    return redirect(
        "pareceres:parecer_detalhe",
        pk=parecer.pk,
    )


@login_required
def item_revisar(request, pk):
    item = get_object_or_404(
        itens_parecer_permitidos(
            request.user
        ),
        pk=pk,
    )

    _exigir_parecer_editavel(
        item.parecer
    )

    if request.method == "POST":
        conclusao_anterior = item.conclusao_item

        form = ItemParecerRevisaoForm(
            request.POST,
            instance=item,
        )

        if form.is_valid():
            objeto = form.save(
                commit=False
            )

            objeto.full_clean()
            objeto.save()

            registrar_revisao_item(
                item=objeto,
                usuario=request.user,
                conclusao_anterior=conclusao_anterior,
            )

            messages.success(
                request,
                "Revisão humana do item salva com sucesso.",
            )

            return redirect(
                "pareceres:parecer_detalhe",
                pk=objeto.parecer_id,
            )
    else:
        form = ItemParecerRevisaoForm(
            instance=item
        )

    return render(
        request,
        "pareceres/item_revisao.html",
        {
            "item": item,
            "parecer": item.parecer,
            "form": form,
        },
    )
