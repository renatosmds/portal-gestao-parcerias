import csv
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render

from apps.core.acesso import (
    empresa_do_usuario,
    usuario_pode_ver_todas_empresas,
)
from apps.core.permissoes_modulos import exigir_modulo

from .catalogo import CATALOGO_RELATORIOS


def relatorios_autorizados(user):
    grupos = OrderedDict()

    for slug, cfg in CATALOGO_RELATORIOS.items():

        if not user.has_perm(
            cfg["permissao"]
        ):
            continue

        grupo = cfg["grupo"]

        grupos.setdefault(
            grupo,
            []
        )

        grupos[grupo].append(
            {
                "slug": slug,
                "titulo": cfg["titulo"],
                "permissao": cfg["permissao"],
            }
        )

    return grupos


def _configuracao(slug):

    cfg = CATALOGO_RELATORIOS.get(
        slug
    )

    if not cfg:
        raise Http404(
            "Relatório não encontrado."
        )

    return cfg


def _modelo(cfg):

    app_label, model_name = cfg[
        "modelo"
    ].split(
        ".",
        1,
    )

    Model = apps.get_model(
        app_label,
        model_name,
    )

    if Model is None:
        raise Http404(
            "Modelo do relatório não encontrado."
        )

    return Model


def _verificar_permissao(
    request,
    cfg,
):
    if not request.user.has_perm(
        cfg["permissao"]
    ):
        raise PermissionDenied


def _aplicar_escopo(
    queryset,
    request,
    empresa_campo,
):
    if not empresa_campo:
        return queryset

    global_scope = (
        usuario_pode_ver_todas_empresas(
            request.user
        )
    )

    empresa_get = request.GET.get(
        "empresa",
        ""
    ).strip()

    if global_scope:

        if not empresa_get.isdigit():
            return queryset

        empresa_id = int(
            empresa_get
        )

        if empresa_campo == "pk":
            return queryset.filter(
                pk=empresa_id
            )

        return queryset.filter(
            **{
                f"{empresa_campo}_id":
                empresa_id
            }
        )

    empresa = empresa_do_usuario(
        request.user
    )

    if not empresa:
        return queryset.none()

    if empresa_campo == "pk":
        return queryset.filter(
            pk=empresa.pk
        )

    return queryset.filter(
        **{
            empresa_campo: empresa
        }
    )


def _campos_pesquisaveis(
    Model,
    colunas,
):
    campos = []

    for nome, _titulo in colunas:

        if "__" in nome:
            continue

        try:
            campo = Model._meta.get_field(
                nome
            )
        except Exception:
            continue

        tipo = campo.get_internal_type()

        if tipo in {
            "CharField",
            "TextField",
            "EmailField",
            "SlugField",
        }:
            campos.append(
                nome
            )

    return campos


def _aplicar_busca(
    queryset,
    Model,
    colunas,
    termo,
):
    termo = (
        termo
        or ""
    ).strip()

    if not termo:
        return queryset

    campos = _campos_pesquisaveis(
        Model,
        colunas,
    )

    if not campos:
        return queryset

    filtro = Q()

    for campo in campos:
        filtro |= Q(
            **{
                f"{campo}__icontains":
                termo
            }
        )

    return queryset.filter(
        filtro
    )


def _valor_campo(
    objeto,
    nome,
):
    atual = objeto

    for parte in nome.split("__"):

        if atual is None:
            return ""

        atual = getattr(
            atual,
            parte,
            ""
        )

        if callable(atual):
            try:
                atual = atual()
            except TypeError:
                pass

    return atual


def _valor_exibicao(
    objeto,
    nome,
):
    if "__" not in nome:

        metodo = getattr(
            objeto,
            f"get_{nome}_display",
            None,
        )

        if callable(metodo):
            try:
                return metodo()
            except Exception:
                pass

    valor = _valor_campo(
        objeto,
        nome,
    )

    if valor is None:
        return ""

    if isinstance(
        valor,
        bool,
    ):
        return (
            "Sim"
            if valor
            else "Não"
        )

    if isinstance(
        valor,
        datetime,
    ):
        return valor.strftime(
            "%d/%m/%Y %H:%M"
        )

    if isinstance(
        valor,
        date,
    ):
        return valor.strftime(
            "%d/%m/%Y"
        )

    if isinstance(
        valor,
        Decimal,
    ):
        return f"{valor:.2f}"

    return str(
        valor
    )


def _linhas(
    queryset,
    colunas,
):
    for objeto in queryset:

        yield [
            _valor_exibicao(
                objeto,
                nome,
            )
            for nome, _titulo
            in colunas
        ]


@login_required
@exigir_modulo("relatorios")
def relatorio_generico(
    request,
    slug,
):
    cfg = _configuracao(
        slug
    )

    _verificar_permissao(
        request,
        cfg,
    )

    Model = _modelo(
        cfg
    )

    queryset = Model.objects.all()

    queryset = _aplicar_escopo(
        queryset,
        request,
        cfg.get(
            "empresa_campo"
        ),
    )

    busca = request.GET.get(
        "q",
        ""
    )

    queryset = _aplicar_busca(
        queryset,
        Model,
        cfg["colunas"],
        busca,
    )

    queryset = queryset.order_by(
        Model._meta.pk.name
    )

    linhas = list(
        _linhas(
            queryset,
            cfg["colunas"],
        )
    )

    contexto = {
        "slug_relatorio": slug,
        "titulo_relatorio":
            cfg["titulo"],
        "grupo_relatorio":
            cfg["grupo"],
        "cabecalhos": [
            titulo
            for _campo, titulo
            in cfg["colunas"]
        ],
        "linhas": linhas,
        "total_registros":
            len(linhas),
        "busca": busca,
        "pode_filtrar_empresa":
            bool(
                cfg.get(
                    "empresa_campo"
                )
                and
                usuario_pode_ver_todas_empresas(
                    request.user
                )
            ),
    }

    if contexto[
        "pode_filtrar_empresa"
    ]:
        Empresa = apps.get_model(
            "empresas",
            "Empresa",
        )

        contexto[
            "empresas_filtro"
        ] = Empresa.objects.order_by(
            "nome"
        )

    return render(
        request,
        "relatorios/generico.html",
        contexto,
    )


@login_required
@exigir_modulo("relatorios")
def relatorio_generico_csv(
    request,
    slug,
):
    cfg = _configuracao(
        slug
    )

    _verificar_permissao(
        request,
        cfg,
    )

    Model = _modelo(
        cfg
    )

    queryset = Model.objects.all()

    queryset = _aplicar_escopo(
        queryset,
        request,
        cfg.get(
            "empresa_campo"
        ),
    )

    queryset = _aplicar_busca(
        queryset,
        Model,
        cfg["colunas"],
        request.GET.get(
            "q",
            ""
        ),
    )

    queryset = queryset.order_by(
        Model._meta.pk.name
    )

    response = HttpResponse(
        content_type=(
            "text/csv; charset=utf-8"
        )
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; filename="'
        f'{slug}.csv"'
    )

    response.write(
        "\ufeff"
    )

    writer = csv.writer(
        response,
        delimiter=";",
    )

    writer.writerow(
        [
            titulo
            for _campo, titulo
            in cfg["colunas"]
        ]
    )

    for linha in _linhas(
        queryset,
        cfg["colunas"],
    ):
        writer.writerow(
            linha
        )

    return response
