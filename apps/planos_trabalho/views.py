from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    ItemPlanoTrabalhoForm,
    PlanoTrabalhoForm,
)

from .models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)


@login_required
def plano_lista(request):
    planos = (
        PlanoTrabalho.objects
        .select_related("termo")
        .prefetch_related("itens")
        .all()
    )

    return render(
        request,
        "planos_trabalho/plano_lista.html",
        {
            "planos": planos,
        },
    )


@login_required
def plano_detalhe(request, pk):
    plano = get_object_or_404(
        PlanoTrabalho.objects
        .select_related("termo")
        .prefetch_related("itens"),
        pk=pk,
    )

    return render(
        request,
        "planos_trabalho/plano_detalhe.html",
        {
            "plano": plano,
            "itens": plano.itens.all(),
        },
    )


@login_required
def plano_criar(request):

    if request.method == "POST":
        form = PlanoTrabalhoForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            plano = form.save()

            return redirect(
                "planos_trabalho:plano_detalhe",
                pk=plano.pk,
            )

    else:
        form = PlanoTrabalhoForm()

    return render(
        request,
        "planos_trabalho/plano_form.html",
        {
            "form": form,
            "titulo": "Novo Plano de Trabalho",
        },
    )


@login_required
def plano_editar(request, pk):
    plano = get_object_or_404(
        PlanoTrabalho,
        pk=pk,
    )

    if request.method == "POST":
        form = PlanoTrabalhoForm(
            request.POST,
            request.FILES,
            instance=plano,
        )

        if form.is_valid():
            plano = form.save()

            return redirect(
                "planos_trabalho:plano_detalhe",
                pk=plano.pk,
            )

    else:
        form = PlanoTrabalhoForm(
            instance=plano
        )

    return render(
        request,
        "planos_trabalho/plano_form.html",
        {
            "form": form,
            "titulo": "Editar Plano de Trabalho",
            "plano": plano,
        },
    )


@login_required
def item_criar(request, plano_pk):
    plano = get_object_or_404(
        PlanoTrabalho,
        pk=plano_pk,
    )

    if request.method == "POST":
        form = ItemPlanoTrabalhoForm(
            request.POST
        )

        if form.is_valid():
            item = form.save(
                commit=False
            )

            item.plano = plano
            item.save()

            return redirect(
                "planos_trabalho:plano_detalhe",
                pk=plano.pk,
            )

    else:
        form = ItemPlanoTrabalhoForm()

    return render(
        request,
        "planos_trabalho/item_form.html",
        {
            "form": form,
            "plano": plano,
            "titulo": "Novo Item do Plano",
        },
    )


@login_required
def item_editar(request, pk):
    item = get_object_or_404(
        ItemPlanoTrabalho.objects.select_related(
            "plano"
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = ItemPlanoTrabalhoForm(
            request.POST,
            instance=item,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "planos_trabalho:plano_detalhe",
                pk=item.plano.pk,
            )

    else:
        form = ItemPlanoTrabalhoForm(
            instance=item
        )

    return render(
        request,
        "planos_trabalho/item_form.html",
        {
            "form": form,
            "plano": item.plano,
            "item": item,
            "titulo": "Editar Item do Plano",
        },
    )
