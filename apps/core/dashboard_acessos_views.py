from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.dashboard_permissoes import modulos_dashboard_usuario
from apps.core.dashboard_widgets import WIDGETS_DASHBOARD
from apps.core.dashboard_widgets_permissoes import widgets_dashboard_usuario
from apps.core.models import (
    ConfiguracaoDashboardGrupo,
    ConfiguracaoDashboardUsuario,
    ConfiguracaoDashboardWidgetGrupo,
    ConfiguracaoDashboardWidgetUsuario,
)
from apps.core.permissoes_modulos import MODULOS, modulos_liberados


User = get_user_model()


NOMES_MODULOS_DASHBOARD = {
    "empresas": "Empresas",
    "departamentos": "Departamentos",
    "fornecedores": "Fornecedores",
    "funcionarios": "Funcion?rios",
    "folha_ponto": "Folha de Ponto",
    "folha_pagamento": "Folha de Pagamento",
    "banco_horas": "Banco de Horas",
    "execucao": "Execu??o",
    "financeiro": "Financeiro",
    "diligencias": "Dilig?ncias",
    "importacoes": "Importa??es",
    "conciliacao": "Concilia??o",
    "metas": "Metas e Indicadores",
    "pareceres": "Pareceres",
    "planos_trabalho": "Planos de Trabalho",
    "assistente_ia": "Assistente IA",
    "documentos": "Documentos",
    "lancamentos": "Lan?amentos",
    "analises": "An?lises",
    "prestacoes": "Presta??es de Contas",
    "termos": "Termos",
    "parcerias": "Parcerias",
    "treinamento": "Treinamento",
    "suporte": "Suporte",
    "cursos": "Cursos",
    "relatorios": "Relat?rios",
}


def _somente_superusuario(request):
    if not request.user.is_superuser:
        raise PermissionDenied


def _nome_modulo(modulo):
    return NOMES_MODULOS_DASHBOARD.get(
        modulo,
        modulo.replace("_", " ").title(),
    )


def _configuracoes_usuario(usuario):
    return {
        item.modulo: item.estado
        for item in ConfiguracaoDashboardUsuario.objects.filter(
            usuario=usuario
        )
    }


def _configuracoes_grupos_usuario(usuario):
    resultado = {}

    configuracoes = (
        ConfiguracaoDashboardGrupo.objects
        .filter(
            grupo__user=usuario,
        )
        .values(
            "modulo",
            "exibir",
        )
    )

    for item in configuracoes:
        resultado.setdefault(
            item["modulo"],
            [],
        ).append(
            item["exibir"]
        )

    return resultado


def _estado_grupo_efetivo(valores):
    if not valores:
        return "Padr?o"

    if any(valores):
        return "Mostrar"

    return "Ocultar"


def _configuracoes_widgets_usuario(usuario):
    return {
        item.widget: item.estado
        for item in ConfiguracaoDashboardWidgetUsuario.objects.filter(
            usuario=usuario
        )
    }


def _configuracoes_widgets_grupos_usuario(usuario):
    resultado = {}

    configuracoes = (
        ConfiguracaoDashboardWidgetGrupo.objects
        .filter(
            grupo__in=usuario.groups.all()
        )
        .values(
            "widget",
            "exibir",
        )
    )

    for item in configuracoes:
        resultado.setdefault(
            item["widget"],
            [],
        ).append(
            item["exibir"]
        )

    return resultado


def _estado_widget_grupo_efetivo(valores):
    if not valores:
        return "Padr?o"

    if any(valores):
        return "Mostrar"

    return "Ocultar"


@login_required
def dashboard_acessos_painel(request):
    _somente_superusuario(request)

    usuarios = (
        User.objects
        .prefetch_related(
            "groups",
            "user_permissions",
        )
        .order_by("username")
    )

    linhas = []

    for usuario in usuarios:
        acessos = set(
            modulos_liberados(usuario)
        )

        dashboard_efetivo = set(
            modulos_dashboard_usuario(usuario)
        )

        individuais = _configuracoes_usuario(
            usuario
        )

        grupos_usuario = _configuracoes_grupos_usuario(
            usuario
        )

        modulos_usuario = []

        for modulo in MODULOS:
            estado_individual = individuais.get(
                modulo
            )

            if (
                estado_individual
                == ConfiguracaoDashboardUsuario.Estado.MOSTRAR
            ):
                individual_texto = "Mostrar"
            elif (
                estado_individual
                == ConfiguracaoDashboardUsuario.Estado.OCULTAR
            ):
                individual_texto = "Ocultar"
            else:
                individual_texto = "Herdar"

            grupo_texto = _estado_grupo_efetivo(
                grupos_usuario.get(
                    modulo,
                    [],
                )
            )

            modulos_usuario.append(
                {
                    "modulo": modulo,
                    "nome": _nome_modulo(modulo),
                    "acesso": modulo in acessos,
                    "individual": individual_texto,
                    "grupo": grupo_texto,
                    "efetivo": modulo in dashboard_efetivo,
                }
            )

        linhas.append(
            {
                "usuario": usuario,
                "modulos": modulos_usuario,
            }
        )

    grupos = Group.objects.order_by(
        "name"
    )

    return render(
        request,
        "core/dashboard_acessos_painel.html",
        {
            "linhas": linhas,
            "grupos": grupos,
        },
    )


@login_required
@transaction.atomic
def dashboard_acessos_usuario(request, pk):
    _somente_superusuario(request)

    usuario = get_object_or_404(
        User,
        pk=pk,
    )

    if request.method == "POST":

        for modulo in MODULOS:
            valor = request.POST.get(
                f"dashboard_{modulo}",
                "herdar",
            )

            if valor == "herdar":
                ConfiguracaoDashboardUsuario.objects.filter(
                    usuario=usuario,
                    modulo=modulo,
                ).delete()
                continue

            if valor not in {
                ConfiguracaoDashboardUsuario.Estado.MOSTRAR,
                ConfiguracaoDashboardUsuario.Estado.OCULTAR,
            }:
                continue

            ConfiguracaoDashboardUsuario.objects.update_or_create(
                usuario=usuario,
                modulo=modulo,
                defaults={
                    "estado": valor,
                },
            )

        for widget in WIDGETS_DASHBOARD:
            valor = request.POST.get(
                f"widget_{widget}",
            )

            # Campos ausentes nao alteram configuracoes existentes.
            if valor is None:
                continue

            if valor == "herdar":
                ConfiguracaoDashboardWidgetUsuario.objects.filter(
                    usuario=usuario,
                    widget=widget,
                ).delete()
                continue

            if valor not in {
                ConfiguracaoDashboardWidgetUsuario.Estado.MOSTRAR,
                ConfiguracaoDashboardWidgetUsuario.Estado.OCULTAR,
            }:
                continue

            ConfiguracaoDashboardWidgetUsuario.objects.update_or_create(
                usuario=usuario,
                widget=widget,
                defaults={
                    "estado": valor,
                },
            )

        messages.success(
            request,
            "Configura??o do Dashboard do usu?rio atualizada.",
        )

        return redirect(
            "dashboard_acessos_usuario",
            pk=usuario.pk,
        )

    configuracoes = _configuracoes_usuario(
        usuario
    )

    acessos = set(
        modulos_liberados(usuario)
    )

    efetivos = set(
        modulos_dashboard_usuario(usuario)
    )

    grupos_usuario = _configuracoes_grupos_usuario(
        usuario
    )

    modulos = []

    for modulo in MODULOS:
        modulos.append(
            {
                "chave": modulo,
                "nome": _nome_modulo(modulo),
                "estado": configuracoes.get(
                    modulo,
                    "herdar",
                ),
                "acesso": modulo in acessos,
                "grupo": _estado_grupo_efetivo(
                    grupos_usuario.get(
                        modulo,
                        [],
                    )
                ),
                "efetivo": modulo in efetivos,
            }
        )

    configuracoes_widgets = (
        _configuracoes_widgets_usuario(
            usuario
        )
    )

    grupos_widgets = (
        _configuracoes_widgets_grupos_usuario(
            usuario
        )
    )

    widgets_efetivos = set(
        widgets_dashboard_usuario(
            usuario
        )
    )

    widgets = []

    for widget, nome in WIDGETS_DASHBOARD.items():
        widgets.append(
            {
                "chave": widget,
                "nome": nome,
                "estado": configuracoes_widgets.get(
                    widget,
                    "herdar",
                ),
                "grupo": _estado_widget_grupo_efetivo(
                    grupos_widgets.get(
                        widget,
                        [],
                    )
                ),
                "efetivo": widget in widgets_efetivos,
            }
        )

    return render(
        request,
        "core/dashboard_acessos_usuario.html",
        {
            "usuario_alvo": usuario,
            "modulos": modulos,
            "widgets": widgets,
        },
    )


@login_required
@transaction.atomic
def dashboard_acessos_grupo(request, pk):
    _somente_superusuario(request)

    grupo = get_object_or_404(
        Group,
        pk=pk,
    )

    if request.method == "POST":

        for modulo in MODULOS:
            valor = request.POST.get(
                f"dashboard_{modulo}",
                "padrao",
            )

            if valor == "padrao":
                ConfiguracaoDashboardGrupo.objects.filter(
                    grupo=grupo,
                    modulo=modulo,
                ).delete()
                continue

            if valor not in {
                "mostrar",
                "ocultar",
            }:
                continue

            ConfiguracaoDashboardGrupo.objects.update_or_create(
                grupo=grupo,
                modulo=modulo,
                defaults={
                    "exibir": valor == "mostrar",
                },
            )

        for widget in WIDGETS_DASHBOARD:
            valor = request.POST.get(
                f"widget_{widget}",
            )

            # Campos ausentes nao alteram configuracoes existentes.
            if valor is None:
                continue

            if valor == "padrao":
                ConfiguracaoDashboardWidgetGrupo.objects.filter(
                    grupo=grupo,
                    widget=widget,
                ).delete()
                continue

            if valor not in {
                "mostrar",
                "ocultar",
            }:
                continue

            ConfiguracaoDashboardWidgetGrupo.objects.update_or_create(
                grupo=grupo,
                widget=widget,
                defaults={
                    "exibir": valor == "mostrar",
                },
            )

        messages.success(
            request,
            "Configura??o do Dashboard do grupo atualizada.",
        )

        return redirect(
            "dashboard_acessos_grupo",
            pk=grupo.pk,
        )

    configuracoes = {
        item.modulo: item.exibir
        for item in ConfiguracaoDashboardGrupo.objects.filter(
            grupo=grupo
        )
    }

    modulos = []

    for modulo in MODULOS:
        if modulo not in configuracoes:
            estado = "padrao"
        elif configuracoes[modulo]:
            estado = "mostrar"
        else:
            estado = "ocultar"

        modulos.append(
            {
                "chave": modulo,
                "nome": _nome_modulo(modulo),
                "estado": estado,
            }
        )

    configuracoes_widgets = {
        item.widget: item.exibir
        for item in ConfiguracaoDashboardWidgetGrupo.objects.filter(
            grupo=grupo
        )
    }

    widgets = []

    for widget, nome in WIDGETS_DASHBOARD.items():

        if widget not in configuracoes_widgets:
            estado = "padrao"
        elif configuracoes_widgets[widget]:
            estado = "mostrar"
        else:
            estado = "ocultar"

        widgets.append(
            {
                "chave": widget,
                "nome": nome,
                "estado": estado,
            }
        )

    return render(
        request,
        "core/dashboard_acessos_grupo.html",
        {
            "grupo": grupo,
            "modulos": modulos,
            "widgets": widgets,
        },
    )
