from apps.core.permissoes_modulos import exigir_modulo
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.lancamentos.models import Lancamento
from apps.regras.engine import motor_regras

from .escopo import (
    itens_permitidos,
    planos_permitidos,
)
from .forms import (
    ItemPlanoTrabalhoForm,
    PlanoTrabalhoForm,
)
from .models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
    VinculoLancamentoItemPlano,
)

from .vinculos import vincular_lancamento_item


@login_required
@exigir_modulo("planos_trabalho")
def plano_lista(request):
    planos = (
        planos_permitidos(
            request.user
        )
        .prefetch_related("itens")
        .order_by(
            "termo_id",
            "-versao",
        )
    )

    return render(
        request,
        "planos_trabalho/plano_lista.html",
        {
            "planos": planos,
        },
    )


@login_required
@exigir_modulo("planos_trabalho")
def plano_detalhe(request, pk):
    plano = get_object_or_404(
        planos_permitidos(
            request.user
        ).prefetch_related(
            "itens"
        ),
        pk=pk,
    )

    itens = (
        plano.itens
        .select_related("meta")
        .order_by(
            "codigo",
            "pk",
        )
    )

    return render(
        request,
        "planos_trabalho/plano_detalhe.html",
        {
            "plano": plano,
            "itens": itens,
        },
    )


@login_required
@exigir_modulo("planos_trabalho")
def plano_criar(request):
    if request.method == "POST":
        form = PlanoTrabalhoForm(
            request.POST,
            request.FILES,
            user=request.user,
        )

        if form.is_valid():
            plano = form.save()

            return redirect(
                "planos_trabalho:plano_detalhe",
                pk=plano.pk,
            )

    else:
        form = PlanoTrabalhoForm(
            user=request.user
        )

    return render(
        request,
        "planos_trabalho/plano_form.html",
        {
            "form": form,
            "titulo": "Novo Plano de Trabalho",
        },
    )


@login_required
@exigir_modulo("planos_trabalho")
def plano_editar(request, pk):
    plano = get_object_or_404(
        planos_permitidos(
            request.user
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = PlanoTrabalhoForm(
            request.POST,
            request.FILES,
            instance=plano,
            user=request.user,
        )

        if form.is_valid():
            plano = form.save()

            return redirect(
                "planos_trabalho:plano_detalhe",
                pk=plano.pk,
            )

    else:
        form = PlanoTrabalhoForm(
            instance=plano,
            user=request.user,
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
@exigir_modulo("planos_trabalho")
def item_criar(request, plano_pk):
    plano = get_object_or_404(
        planos_permitidos(
            request.user
        ),
        pk=plano_pk,
    )

    if request.method == "POST":
        form = ItemPlanoTrabalhoForm(
            request.POST,
            user=request.user,
            plano=plano,
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
        form = ItemPlanoTrabalhoForm(
            user=request.user,
            plano=plano,
        )

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
@exigir_modulo("planos_trabalho")
def item_editar(request, pk):
    item = get_object_or_404(
        itens_permitidos(
            request.user
        ),
        pk=pk,
    )

    if request.method == "POST":
        form = ItemPlanoTrabalhoForm(
            request.POST,
            instance=item,
            user=request.user,
            plano=item.plano,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "planos_trabalho:plano_detalhe",
                pk=item.plano.pk,
            )

    else:
        form = ItemPlanoTrabalhoForm(
            instance=item,
            user=request.user,
            plano=item.plano,
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


@login_required
@exigir_modulo("planos_trabalho")
def plano_analise(request, pk):
    plano = get_object_or_404(
        planos_permitidos(
            request.user
        ),
        pk=pk,
    )

    resultado = (
        motor_regras
        .analisar_plano_trabalho_completo(
            plano
        )
    )

    return render(
        request,
        "planos_trabalho/plano_analise.html",
        {
            "plano": plano,
            "resultado": resultado,
            "resumo": (
                resultado.resumo_executivo
            ),
        },
    )


@login_required
@exigir_modulo("planos_trabalho")
def item_analise(request, pk):
    item = get_object_or_404(
        itens_permitidos(
            request.user
        ),
        pk=pk,
    )

    resultado = (
        motor_regras
        .analisar_item_plano_completo(
            item
        )
    )

    return render(
        request,
        "planos_trabalho/item_analise.html",
        {
            "item": item,
            "plano": item.plano,
            "resultado": resultado,
            "resumo": (
                resultado.resumo_executivo
            ),
        },
    )



@login_required
@exigir_modulo("planos_trabalho")
@permission_required(
    "planos_trabalho.change_vinculolancamentoitemplano",
    raise_exception=True,
)
def item_vinculos(request, pk):
    item = get_object_or_404(
        itens_permitidos(
            request.user
        ).select_related(
            "plano",
            "plano__termo",
            "plano__termo__empresa",
        ),
        pk=pk,
    )

    termo = item.plano.termo

    lancamentos = (
        Lancamento.objects
        .filter(
            termo=termo,
            empresa=termo.empresa,
        )
        .order_by(
            "data_documento",
            "pk",
        )
    )

    vinculos_ativos = {
        vinculo.lancamento_id: vinculo
        for vinculo in (
            VinculoLancamentoItemPlano.objects
            .filter(
                lancamento__in=lancamentos,
                ativo=True,
            )
            .select_related(
                "item_plano",
                "item_plano__plano",
            )
        )
    }

    if request.method == "POST":
        selecionados = {
            int(valor)
            for valor in request.POST.getlist(
                "lancamentos"
            )
            if valor.isdigit()
        }

        justificativa = (
            request.POST.get(
                "justificativa",
                "",
            )
            or ""
        ).strip()

        ids_validos = set(
            lancamentos.values_list(
                "pk",
                flat=True,
            )
        )

        selecionados &= ids_validos

        with transaction.atomic():
            for lancamento in lancamentos:
                atual = vinculos_ativos.get(
                    lancamento.pk
                )

                if lancamento.pk in selecionados:
                    if (
                        atual
                        and atual.item_plano_id
                        == item.pk
                    ):
                        continue

                    vincular_lancamento_item(
                        lancamento,
                        item,
                        justificativa=(
                            justificativa
                            or (
                                "Vinculo manual realizado "
                                "na gestao do Plano de Trabalho."
                            )
                        ),
                        quantidade_executada=1,
                        valor_unitario_executado=(
                            lancamento.valor_documento
                        ),
                        unidade_executada=(
                            item.unidade or "unidade"
                        ),
                    )

                elif (
                    atual
                    and atual.item_plano_id == item.pk
                ):
                    atual.ativo = False
                    atual.save(
                        update_fields=["ativo"]
                    )

        return redirect(
            "planos_trabalho:item_analise",
            pk=item.pk,
        )

    linhas = []

    for lancamento in lancamentos:
        atual = vinculos_ativos.get(
            lancamento.pk
        )

        linhas.append(
            {
                "lancamento": lancamento,
                "selecionado": bool(
                    atual
                    and atual.item_plano_id
                    == item.pk
                ),
                "vinculado_outro": bool(
                    atual
                    and atual.item_plano_id
                    != item.pk
                ),
                "item_atual": (
                    atual.item_plano
                    if atual
                    else None
                ),
            }
        )

    return render(
        request,
        "planos_trabalho/item_vinculos.html",
        {
            "item": item,
            "plano": item.plano,
            "linhas": linhas,
        },
    )
