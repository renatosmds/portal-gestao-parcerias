from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

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


def _exigir_parecer_editavel(parecer):
    permitidas = {
        ParecerTecnico.Situacao.RASCUNHO,
        ParecerTecnico.Situacao.EM_REVISAO,
    }

    if parecer.situacao not in permitidas:
        raise PermissionDenied(
            "Este parecer n?o est? dispon?vel para revis?o."
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

    contexto = {
        "parecer": parecer,
        "itens": itens,
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

            messages.success(
                request,
                "Revis?o humana do parecer salva com sucesso.",
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

            messages.success(
                request,
                "Revis?o humana do item salva com sucesso.",
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
