from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.core.acesso import filtrar_por_empresa
from apps.core.permissoes_modulos import exigir_modulo

from .forms_banco_horas import (
    RegimeBancoHorasForm,
)
from .models import (
    Funcionario,
    RegimeBancoHoras,
)


def _regimes_queryset(request):
    """
    Escopo multiempresa central.
    """

    queryset = (
        RegimeBancoHoras.objects
        .select_related(
            "funcionario",
            "funcionario__empresa",
        )
        .order_by(
            "funcionario__nome",
            "-data_inicio",
            "-pk",
        )
    )

    return filtrar_por_empresa(
        queryset,
        request.user,
        campo="funcionario__empresa",
    )


def _funcionarios_queryset(request):

    queryset = (
        Funcionario.objects
        .select_related("empresa")
        .filter(ativo=True)
        .order_by("nome")
    )

    return filtrar_por_empresa(
        queryset,
        request.user,
    )


@login_required
@exigir_modulo("banco_horas")
@permission_required(
    "funcionarios.view_regimebancohoras",
    raise_exception=True,
)
def regimes_banco_horas_list(request):

    regimes = _regimes_queryset(
        request
    )

    funcionarios = (
        _funcionarios_queryset(
            request
        )
    )

    funcionario_id = (
        request.GET.get(
            "funcionario"
        )
        or ""
    )

    situacao = (
        request.GET.get(
            "situacao"
        )
        or ""
    )

    if funcionario_id.isdigit():
        regimes = regimes.filter(
            funcionario_id=int(
                funcionario_id
            )
        )

    if situacao == "ativos":
        regimes = regimes.filter(
            ativo=True
        )

    elif situacao == "inativos":
        regimes = regimes.filter(
            ativo=False
        )

    return render(
        request,
        (
            "funcionarios/"
            "regimes_banco_horas_list.html"
        ),
        {
            "regimes": regimes,
            "funcionarios": funcionarios,
            "funcionario_selecionado": (
                funcionario_id
            ),
            "situacao_selecionada": (
                situacao
            ),
            "pode_adicionar": (
                request.user.is_superuser
                or request.user.has_perm(
                    (
                        "funcionarios."
                        "add_regimebancohoras"
                    )
                )
            ),
            "pode_editar": (
                request.user.is_superuser
                or request.user.has_perm(
                    (
                        "funcionarios."
                        "change_regimebancohoras"
                    )
                )
            ),
        },
    )


@login_required
@exigir_modulo("banco_horas")
@permission_required(
    "funcionarios.add_regimebancohoras",
    raise_exception=True,
)
def regime_banco_horas_create(
    request,
):

    form = RegimeBancoHorasForm(
        request.POST or None,
        user=request.user,
    )

    if (
        request.method == "POST"
        and form.is_valid()
    ):

        regime = form.save()

        messages.success(
            request,
            (
                "Regime de Banco de Horas "
                "cadastrado com sucesso."
            ),
        )

        return redirect(
            "regime_banco_horas_update",
            pk=regime.pk,
        )

    return render(
        request,
        (
            "funcionarios/"
            "regime_banco_horas_form.html"
        ),
        {
            "form": form,
            "object": None,
        },
    )


@login_required
@exigir_modulo("banco_horas")
@permission_required(
    "funcionarios.change_regimebancohoras",
    raise_exception=True,
)
def regime_banco_horas_update(
    request,
    pk,
):

    regime = get_object_or_404(
        _regimes_queryset(
            request
        ),
        pk=pk,
    )

    form = RegimeBancoHorasForm(
        request.POST or None,
        instance=regime,
        user=request.user,
    )

    if (
        request.method == "POST"
        and form.is_valid()
    ):

        form.save()

        messages.success(
            request,
            (
                "Regime de Banco de Horas "
                "atualizado com sucesso."
            ),
        )

        return redirect(
            "regime_banco_horas_update",
            pk=regime.pk,
        )

    return render(
        request,
        (
            "funcionarios/"
            "regime_banco_horas_form.html"
        ),
        {
            "form": form,
            "object": regime,
        },
    )
