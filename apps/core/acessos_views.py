from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.permissoes_modulos import MODULOS


User = get_user_model()


NOMES_MODULOS = {
    "empresas": "Empresas / OSCs",
    "departamentos": "Departamentos",
    "fornecedores": "Fornecedores",
    "funcionarios": "Empregados",
    "folha_ponto": "Folha de Ponto",
    "folha_pagamento": "Contracheques",
    "banco_horas": "Banco de Horas",
    "execucao": "Execução",
    "financeiro": "Financeiro",
    "diligencias": "Diligências",
    "importacoes": "Importações",
    "conciliacao": "Conciliação Bancária",
    "metas": "Metas e Indicadores",
    "pareceres": "Pareceres Técnicos",
    "planos_trabalho": "Planos de Trabalho",
    "assistente_ia": "Análise Assistida",
    "documentos": "Documentos",
    "lancamentos": "Lançamentos",
    "analises": "Análises",
    "prestacoes": "Prestações de Contas",
    "termos": "Termos",
    "parcerias": "Parcerias",
    "treinamento": "Central de Treinamento",
    "suporte": "Suporte e Conhecimento",
    "cursos": "Cursos",
    "relatorios": "Relatórios",
}


# Relatorios nao possui permissao propria.
MODULOS_DERIVADOS = {
    "relatorios",
}


def _somente_superusuario(request):
    if not request.user.is_superuser:
        raise PermissionDenied


def _permission_por_codigo(codigo):
    app_label, codename = codigo.split(".", 1)

    return Permission.objects.get(
        content_type__app_label=app_label,
        codename=codename,
    )


def _ids_permissoes_modulos_editaveis():
    ids = set()

    for modulo, codigos in MODULOS.items():
        if modulo in MODULOS_DERIVADOS:
            continue

        for codigo in codigos:
            ids.add(
                _permission_por_codigo(codigo).pk
            )

    return ids


def _modulos_editaveis():
    return [
        {
            "chave": chave,
            "nome": NOMES_MODULOS.get(
                chave,
                chave.replace("_", " ").title(),
            ),
            "permissoes": MODULOS[chave],
        }
        for chave in MODULOS
        if chave not in MODULOS_DERIVADOS
    ]


def _modulos_diretos_usuario(usuario):
    codigos_diretos = {
        f"{p.content_type.app_label}.{p.codename}"
        for p in usuario.user_permissions.select_related(
            "content_type"
        )
    }

    return {
        modulo
        for modulo, codigos in MODULOS.items()
        if any(
            codigo in codigos_diretos
            for codigo in codigos
        )
    }


def _modulos_grupos_usuario(usuario):
    codigos_grupos = {
        f"{p.content_type.app_label}.{p.codename}"
        for p in Permission.objects.filter(
            group__user=usuario
        )
        .select_related("content_type")
        .distinct()
    }

    return {
        modulo
        for modulo, codigos in MODULOS.items()
        if any(
            codigo in codigos_grupos
            for codigo in codigos
        )
    }


def _modulos_grupo(grupo):
    codigos = {
        f"{p.content_type.app_label}.{p.codename}"
        for p in grupo.permissions.select_related(
            "content_type"
        )
    }

    return {
        modulo
        for modulo, permissoes in MODULOS.items()
        if any(
            codigo in codigos
            for codigo in permissoes
        )
    }


@login_required
def acessos_painel(request):
    _somente_superusuario(request)

    usuarios = (
        User.objects
        .prefetch_related(
            "user_permissions",
            "groups",
            "groups__permissions",
        )
        .order_by("username")
    )

    grupos = (
        Group.objects
        .prefetch_related("permissions")
        .order_by("name")
    )

    matriz = []

    for usuario in usuarios:
        diretos = _modulos_diretos_usuario(
            usuario
        )

        por_grupo = _modulos_grupos_usuario(
            usuario
        )

        acessos = []

        for modulo in MODULOS:
            direto = (
                usuario.is_superuser
                or modulo in diretos
            )

            grupo = (
                usuario.is_superuser
                or modulo in por_grupo
            )

            efetivo = (
                usuario.is_superuser
                or direto
                or grupo
            )

            if not efetivo:
                continue

            acessos.append(
                {
                    "modulo": modulo,
                    "nome": NOMES_MODULOS.get(
                        modulo,
                        modulo.replace(
                            "_",
                            " ",
                        ).title(),
                    ),
                    "direto": direto,
                    "grupo": grupo,
                    "efetivo": efetivo,
                    "superusuario": (
                        usuario.is_superuser
                    ),
                }
            )

        matriz.append(
            {
                "usuario": usuario,
                "acessos": acessos,
            }
        )

    return render(
        request,
        "core/acessos_painel.html",
        {
            "usuarios": usuarios,
            "grupos": grupos,
            "matriz": matriz,
        },
    )


@login_required
@transaction.atomic
def acessos_usuario(request, pk):
    _somente_superusuario(request)

    usuario = get_object_or_404(
        User,
        pk=pk,
    )

    if request.method == "POST":
        selecionados = set(
            request.POST.getlist("modulos")
        )

        controladas = (
            _ids_permissoes_modulos_editaveis()
        )

        # Remove apenas as permissoes controladas
        # por esta tela. Outras permissoes Django
        # permanecem intactas.
        usuario.user_permissions.remove(
            *controladas
        )

        for modulo in selecionados:
            if (
                modulo not in MODULOS
                or modulo in MODULOS_DERIVADOS
            ):
                continue

            for codigo in MODULOS[modulo]:
                usuario.user_permissions.add(
                    _permission_por_codigo(
                        codigo
                    )
                )

        messages.success(
            request,
            (
                "Acessos diretos de "
                f"{usuario.get_username()} "
                "atualizados com sucesso."
            ),
        )

        return redirect("acessos_painel")

    diretos = _modulos_diretos_usuario(
        usuario
    )

    grupos = _modulos_grupos_usuario(
        usuario
    )

    return render(
        request,
        "core/acessos_usuario.html",
        {
            "usuario_alvo": usuario,
            "modulos": _modulos_editaveis(),
            "modulos_diretos": diretos,
            "modulos_grupo": grupos,
            "grupos_disponiveis": Group.objects.order_by(
                "name"
            ),
            "grupos_usuario": set(
                usuario.groups.values_list(
                    "pk",
                    flat=True,
                )
            ),
        },
    )


@login_required
@transaction.atomic
def acessos_grupo(request, pk):
    _somente_superusuario(request)

    grupo = get_object_or_404(
        Group,
        pk=pk,
    )

    if request.method == "POST":
        selecionados = set(
            request.POST.getlist("modulos")
        )

        controladas = (
            _ids_permissoes_modulos_editaveis()
        )

        grupo.permissions.remove(
            *controladas
        )

        for modulo in selecionados:
            if (
                modulo not in MODULOS
                or modulo in MODULOS_DERIVADOS
            ):
                continue

            for codigo in MODULOS[modulo]:
                grupo.permissions.add(
                    _permission_por_codigo(
                        codigo
                    )
                )

        messages.success(
            request,
            (
                f"Permissões do grupo "
                f"{grupo.name} atualizadas."
            ),
        )

        return redirect("acessos_painel")

    selecionados = _modulos_grupo(
        grupo
    )

    return render(
        request,
        "core/acessos_grupo.html",
        {
            "grupo": grupo,
            "modulos": _modulos_editaveis(),
            "modulos_selecionados": selecionados,
        },
    )

@login_required
@transaction.atomic
def acessos_grupo_novo(request):
    _somente_superusuario(request)

    if request.method != "POST":
        return redirect("acessos_painel")

    nome = request.POST.get(
        "nome",
        "",
    ).strip()

    if not nome:
        messages.error(
            request,
            "Informe um nome para o grupo.",
        )
        return redirect("acessos_painel")

    if Group.objects.filter(
        name__iexact=nome
    ).exists():
        messages.warning(
            request,
            "Ja existe um grupo com esse nome.",
        )
        return redirect("acessos_painel")

    grupo = Group.objects.create(
        name=nome
    )

    messages.success(
        request,
        f"Grupo {grupo.name} criado com sucesso.",
    )

    return redirect(
        "acessos_grupo",
        pk=grupo.pk,
    )

@login_required
@transaction.atomic
def acessos_usuario_grupos(request, pk):
    _somente_superusuario(request)

    usuario = get_object_or_404(
        User,
        pk=pk,
    )

    if request.method != "POST":
        return redirect(
            "acessos_usuario",
            pk=usuario.pk,
        )

    ids_recebidos = request.POST.getlist(
        "grupos"
    )

    grupos_validos = Group.objects.filter(
        pk__in=ids_recebidos
    )

    usuario.groups.set(
        grupos_validos
    )

    messages.success(
        request,
        (
            "Grupos de "
            f"{usuario.get_username()} "
            "atualizados com sucesso."
        ),
    )

    return redirect(
        "acessos_usuario",
        pk=usuario.pk,
    )

