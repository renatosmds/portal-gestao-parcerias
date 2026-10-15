from apps.core.permissoes_modulos import exigir_modulo
import csv
from decimal import Decimal
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from apps.core.acesso import (
    filtrar_por_empresa,
    usuario_pode_ver_todas_empresas,
)
from apps.diligencias.models import Diligencia
from apps.funcionarios.models import FolhaPagamento, FolhaPonto, Funcionario
from apps.lancamentos.models import Lancamento

from .views_genericos import relatorios_autorizados

def _aplicar_escopo_empresa(
    queryset,
    request,
    campo="empresa",
):
    """
    Aplica a politica central de escopo multiempresa.

    Usuarios globais podem visualizar todas as empresas e,
    opcionalmente, filtrar por ?empresa=<id>.

    Usuarios nao globais ignoram qualquer empresa informada
    na URL e permanecem restritos a propria empresa.
    """
    if usuario_pode_ver_todas_empresas(
        request.user
    ):
        value = request.GET.get(
            "empresa",
            ""
        ).strip()

        if value.isdigit():
            return queryset.filter(
                **{
                    f"{campo}_id": int(value)
                }
            )

        return queryset

    return filtrar_por_empresa(
        queryset,
        request.user,
        campo=campo,
    )


def _permissoes_relatorios(user):
    return {
        "pode_diligencias": user.has_perm(
            "diligencias.view_diligencia"
        ),
        "pode_glosas": user.has_perm(
            "lancamentos.view_lancamento"
        ),
        "pode_funcionarios": user.has_perm(
            "funcionarios.view_funcionario"
        ),
        "pode_folha": user.has_perm(
            "funcionarios.view_folhapagamento"
        ),
    }

def _csv_response(filename, headers, rows):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(headers)
    writer.writerows(rows)
    return response

@login_required
@exigir_modulo("relatorios")
def painel_relatorios(request):
    permissoes = _permissoes_relatorios(
        request.user
    )

    diligencias = _aplicar_escopo_empresa(
        Diligencia.objects.all(),
        request,
    )
    lancamentos = _aplicar_escopo_empresa(
        Lancamento.objects.all(),
        request,
    )
    funcionarios = _aplicar_escopo_empresa(
        Funcionario.objects.all(),
        request,
    )

    contexto = {
        **permissoes,
        "grupos_relatorios": relatorios_autorizados(
            request.user
        ),
        "qtd_diligencias": (
            diligencias.count()
            if permissoes["pode_diligencias"]
            else 0
        ),
        "qtd_diligencias_abertas": (
            diligencias.exclude(
                status__in=[
                    Diligencia.Status.ATENDIDA,
                    Diligencia.Status.NAO_ATENDIDA,
                    Diligencia.Status.CANCELADA,
                ]
            ).count()
            if permissoes["pode_diligencias"]
            else 0
        ),
        "qtd_glosas": (
            lancamentos.exclude(
                tipo_glosa=Lancamento.TipoGlosa.NENHUMA
            ).count()
            if permissoes["pode_glosas"]
            else 0
        ),
        "valor_glosado": (
            lancamentos.aggregate(
                total=Sum("valor_glosa")
            )["total"]
            or Decimal("0.00")
            if permissoes["pode_glosas"]
            else Decimal("0.00")
        ),
        "qtd_funcionarios": (
            funcionarios.count()
            if permissoes["pode_funcionarios"]
            else 0
        ),
        "qtd_folhas_abertas": (
            FolhaPonto.objects.filter(
                funcionario__in=funcionarios,
                status="aberta",
            ).count()
            if permissoes["pode_folha"]
            else 0
        ),
    }
    return render(request, "relatorios/painel.html", contexto)


def _diligencias_qs(request):
    qs = Diligencia.objects.select_related(
        "empresa",
        "responsavel",
        "criada_por",
    )
    qs = _aplicar_escopo_empresa(
        qs,
        request,
    )
    if request.GET.get("status"): qs = qs.filter(status=request.GET["status"])
    if request.GET.get("prioridade"): qs = qs.filter(prioridade=request.GET["prioridade"])
    inicio, fim = request.GET.get("inicio"), request.GET.get("fim")
    if inicio: qs = qs.filter(criado_em__date__gte=inicio)
    if fim: qs = qs.filter(criado_em__date__lte=fim)
    return qs

@login_required
@exigir_modulo("relatorios")
@permission_required(
    "diligencias.view_diligencia",
    raise_exception=True,
)
def relatorio_diligencias(request):
    qs = _diligencias_qs(request)
    return render(request, "relatorios/diligencias.html", {"itens": qs, "status_choices": Diligencia.Status.choices, "prioridade_choices": Diligencia.Prioridade.choices, "hoje": timezone.localdate()})

@login_required
@exigir_modulo("relatorios")
@permission_required(
    "diligencias.view_diligencia",
    raise_exception=True,
)
def relatorio_diligencias_csv(request):
    rows=((d.pk,d.assunto,str(d.empresa or ""),d.get_prioridade_display(),d.prazo_resposta.strftime("%d/%m/%Y") if d.prazo_resposta else "",d.get_status_display(),str(d.responsavel or "")) for d in _diligencias_qs(request))
    return _csv_response("diligencias.csv", ["Código","Assunto","OSC","Prioridade","Prazo","Situação","Responsável"], rows)


def _glosas_qs(request):
    qs = Lancamento.objects.exclude(
        tipo_glosa=Lancamento.TipoGlosa.NENHUMA
    ).select_related(
        "empresa",
        "termo",
        "prestacao",
        "fornecedor",
    )
    qs = _aplicar_escopo_empresa(
        qs,
        request,
    )
    if request.GET.get("tipo_glosa"): qs=qs.filter(tipo_glosa=request.GET["tipo_glosa"])
    inicio,fim=request.GET.get("inicio"),request.GET.get("fim")
    if inicio: qs=qs.filter(data_documento__gte=inicio)
    if fim: qs=qs.filter(data_documento__lte=fim)
    return qs

@login_required
@exigir_modulo("relatorios")
@permission_required(
    "lancamentos.view_lancamento",
    raise_exception=True,
)
def relatorio_glosas(request):
    qs=_glosas_qs(request)
    totais=qs.aggregate(documentos=Sum("valor_documento"), glosas=Sum("valor_glosa"))
    return render(request,"relatorios/glosas.html",{"itens":qs,"tipo_choices":Lancamento.TipoGlosa.choices,"total_documentos":totais["documentos"] or 0,"total_glosas":totais["glosas"] or 0})

@login_required
@exigir_modulo("relatorios")
@permission_required(
    "lancamentos.view_lancamento",
    raise_exception=True,
)
def relatorio_glosas_csv(request):
    rows=((l.numero_lancamento,str(l.empresa),l.data_documento.strftime("%d/%m/%Y"),l.descricao,f"{l.valor_documento:.2f}",l.get_tipo_glosa_display(),f"{l.valor_glosa:.2f}",f"{l.valor_aprovado:.2f}") for l in _glosas_qs(request))
    return _csv_response("demonstrativo_glosas.csv",["Lançamento","OSC","Data","Descrição","Valor documento","Tipo","Valor glosado","Valor reconhecido"],rows)


def _funcionarios_qs(request):
    qs = Funcionario.objects.select_related(
        "empresa",
        "termo",
    ).order_by(
        "nome"
    )
    qs = _aplicar_escopo_empresa(
        qs,
        request,
    )
    if request.GET.get("ativo") in {"0","1"}: qs=qs.filter(ativo=request.GET["ativo"]=="1")
    return qs

@login_required
@exigir_modulo("relatorios")
@permission_required(
    "funcionarios.view_funcionario",
    raise_exception=True,
)
def relatorio_funcionarios(request):
    return render(request,"relatorios/funcionarios.html",{"itens":_funcionarios_qs(request)})

@login_required
@exigir_modulo("relatorios")
@permission_required(
    "funcionarios.view_funcionario",
    raise_exception=True,
)
def relatorio_funcionarios_csv(request):
    rows=((f.nome,f.cpf or "",f.get_tipo_vinculo_display(),f.cargo or "",str(f.empresa or ""),str(f.termo or ""),"Ativo" if f.ativo else "Inativo") for f in _funcionarios_qs(request))
    return _csv_response("funcionarios.csv",["Nome","CPF","Vínculo","Cargo","OSC","Termo","Situação"],rows)


def _folha_qs(request):
    qs = FolhaPagamento.objects.select_related(
        "funcionario",
        "funcionario__empresa",
        "folha_ponto",
    )
    qs = _aplicar_escopo_empresa(
        qs,
        request,
        campo="funcionario__empresa",
    )
    competencia=request.GET.get("competencia")
    if competencia: qs=qs.filter(competencia__startswith=competencia)
    return qs

@login_required
@exigir_modulo("relatorios")
@permission_required(
    "funcionarios.view_folhapagamento",
    raise_exception=True,
)
def relatorio_folha(request):
    itens=list(_folha_qs(request))
    return render(request,"relatorios/folha.html",{"itens":itens,"total_bruto":sum((i.total_proventos for i in itens),Decimal("0")),"total_descontos":sum((i.total_descontos for i in itens),Decimal("0")),"total_liquido":sum((i.valor_liquido for i in itens),Decimal("0"))})

@login_required
@exigir_modulo("relatorios")
@permission_required(
    "funcionarios.view_folhapagamento",
    raise_exception=True,
)
def relatorio_folha_csv(request):
    rows=((f.competencia.strftime("%m/%Y"),f.funcionario.nome,str(f.funcionario.empresa or ""),f"{f.total_proventos:.2f}",f"{f.total_descontos:.2f}",f"{f.valor_liquido:.2f}",f.get_status_display()) for f in _folha_qs(request))
    return _csv_response("folha_consolidada.csv",["Competência","Funcionário","OSC","Proventos","Descontos","Líquido","Situação"],rows)
