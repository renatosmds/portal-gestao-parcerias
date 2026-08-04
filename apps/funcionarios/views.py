import io

import xhtml2pdf.pisa as pisa
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView
from django.views.generic.base import View
from reportlab.pdfgen import canvas

from .forms import FuncionarioForm, FolhaPontoForm, FolhaPagamentoForm
from .mixins import EmpresaAtualMixin, FuncionarioPorEmpresaMixin, PermissaoFuncionarioMixin
from .models import Funcionario, FolhaPonto, FolhaPagamento
from .services import criar_usuario_para_funcionario, get_empresa_do_usuario


class FuncionariosList(PermissaoFuncionarioMixin, FuncionarioPorEmpresaMixin, ListView):
    permission_required = "funcionarios.view_funcionario"
    model = Funcionario
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report_button"] = _("Employee report")
        return context


class FuncionarioEdit(PermissaoFuncionarioMixin, FuncionarioPorEmpresaMixin, UpdateView):
    permission_required = "funcionarios.change_funcionario"
    model = Funcionario
    form_class = FuncionarioForm
    success_url = reverse_lazy("list_funcionarios")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class FuncionarioDelete(PermissaoFuncionarioMixin, FuncionarioPorEmpresaMixin, DeleteView):
    permission_required = "funcionarios.delete_funcionario"
    model = Funcionario
    success_url = reverse_lazy("list_funcionarios")


class FuncionarioCreate(PermissaoFuncionarioMixin, EmpresaAtualMixin, CreateView):
    permission_required = "funcionarios.add_funcionario"
    model = Funcionario
    form_class = FuncionarioForm
    success_url = reverse_lazy("list_funcionarios")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        funcionario = form.save(commit=False)
        if not self.request.user.is_superuser:
            funcionario.empresa = self.empresa_atual
        funcionario.user = criar_usuario_para_funcionario(funcionario.usuario)
        funcionario.save()
        form.save_m2m()
        self.object = funcionario
        return redirect(self.get_success_url())


@login_required
def relatorio_funcionario(request):
    if not request.user.has_perm("funcionarios.view_funcionario"):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    empresa = get_empresa_do_usuario(request.user)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        'attachment; filename="Relatorio_de_Funcionarios.pdf"'
    )

    buffer = io.BytesIO()
    pdf_canvas = canvas.Canvas(buffer)
    pdf_canvas.drawString(200, 810, "Relatório de funcionários")
    pdf_canvas.drawString(0, 800, "_" * 150)

    funcionarios = Funcionario.objects.filter(empresa=empresa)
    linha = "Nome: %s | Hora Extra: %.2f"

    y = 750
    for funcionario in funcionarios:
        if y < 40:
            pdf_canvas.showPage()
            y = 800

        pdf_canvas.drawString(
            10,
            y,
            linha % (funcionario.nome, funcionario.total_horas_extra),
        )
        y -= 20

    pdf_canvas.showPage()
    pdf_canvas.save()

    response.write(buffer.getvalue())
    buffer.close()
    return response


class Render:
    @staticmethod
    def render(path: str, params: dict, filename: str):
        template = get_template(path)
        html = template.render(params)
        response = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), response)

        if not pdf.err:
            result = HttpResponse(
                response.getvalue(),
                content_type="application/pdf",
            )
            result["Content-Disposition"] = (
                f'attachment; filename="{filename}.pdf"'
            )
            return result

        return HttpResponse("Erro ao gerar PDF.", status=400)


class Pdf(PermissaoFuncionarioMixin, EmpresaAtualMixin, View):
    permission_required = "funcionarios.view_funcionario"
    def get(self, request):
        funcionarios = Funcionario.objects.filter(empresa=self.empresa_atual)
        params = {
            "today": "Variável today",
            "sales": "Variável sales",
            "request": request,
            "funcionarios": funcionarios,
        }
        return Render.render(
            "funcionarios/relatorio.html",
            params,
            "Relatório de Funcionários",
        )


class PdfDebug(PermissaoFuncionarioMixin, EmpresaAtualMixin, TemplateView):
    permission_required = "funcionarios.view_funcionario"
    template_name = "funcionarios/relatorio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["funcionarios"] = Funcionario.objects.filter(
            empresa=self.empresa_atual
        )
        return context


def _empresa(request):
    if request.user.is_superuser:
        return None
    return get_empresa_do_usuario(request.user)

def _exigir(request, perm):
    if not (request.user.is_superuser or request.user.has_perm(perm)):
        raise PermissionDenied

def _funcionarios_queryset(request):
    qs = Funcionario.objects.all()
    empresa = _empresa(request)
    return qs if request.user.is_superuser else qs.filter(empresa=empresa)

def _pontos_queryset(request):
    qs = FolhaPonto.objects.select_related("funcionario")
    empresa = _empresa(request)
    return qs if request.user.is_superuser else qs.filter(funcionario__empresa=empresa)

def _pagamentos_queryset(request):
    qs = FolhaPagamento.objects.select_related("funcionario", "folha_ponto")
    empresa = _empresa(request)
    return qs if request.user.is_superuser else qs.filter(funcionario__empresa=empresa)

@login_required
def folhas_ponto_list(request):
    _exigir(request, "funcionarios.view_folhaponto")
    return render(request, "funcionarios/folha_ponto_list.html", {"object_list": _pontos_queryset(request)})

@login_required
def folha_ponto_form(request, pk=None):
    _exigir(request, "funcionarios.change_folhaponto" if pk else "funcionarios.add_folhaponto")
    obj = get_object_or_404(_pontos_queryset(request), pk=pk) if pk else None
    form = FolhaPontoForm(request.POST or None, instance=obj)
    form.fields["funcionario"].queryset = _funcionarios_queryset(request).filter(ativo=True)
    if form.is_valid():
        form.save()
        messages.success(request, "Folha de ponto salva com sucesso.")
        return redirect("folhas_ponto_list")
    return render(request, "funcionarios/folha_ponto_form.html", {"form": form, "object": obj})

@login_required
def fechar_folha_ponto(request, pk):
    _exigir(request, "funcionarios.change_folhaponto")
    obj = get_object_or_404(_pontos_queryset(request), pk=pk)
    if request.method == "POST":
        obj.status = "fechada"
        obj.fechado_em = timezone.now()
        obj.fechado_por = request.user
        obj.save(update_fields=["status", "fechado_em", "fechado_por", "atualizado_em"])
        messages.success(request, "Folha de ponto fechada.")
    return redirect("folhas_ponto_list")

@login_required
def folhas_pagamento_list(request):
    _exigir(request, "funcionarios.view_folhapagamento")
    return render(request, "funcionarios/folha_pagamento_list.html", {"object_list": _pagamentos_queryset(request)})

@login_required
def folha_pagamento_form(request, pk=None):
    _exigir(request, "funcionarios.change_folhapagamento" if pk else "funcionarios.add_folhapagamento")
    obj = get_object_or_404(_pagamentos_queryset(request), pk=pk) if pk else None
    form = FolhaPagamentoForm(request.POST or None, instance=obj)
    form.fields["funcionario"].queryset = _funcionarios_queryset(request).filter(ativo=True)
    pontos = _pontos_queryset(request).filter(status="fechada")
    form.fields["folha_ponto"].queryset = pontos
    if form.is_valid():
        folha = form.save()
        messages.success(request, "Contracheque calculado e salvo.")
        return redirect("folha_pagamento_detail", pk=folha.pk)
    return render(request, "funcionarios/folha_pagamento_form.html", {"form": form, "object": obj})

@login_required
def folha_pagamento_detail(request, pk):
    _exigir(request, "funcionarios.view_folhapagamento")
    obj = get_object_or_404(_pagamentos_queryset(request), pk=pk)
    return render(request, "funcionarios/folha_pagamento_detail.html", {"folha": obj})

@login_required
def fechar_folha_pagamento(request, pk):
    _exigir(request, "funcionarios.change_folhapagamento")
    obj = get_object_or_404(_pagamentos_queryset(request), pk=pk)
    if request.method == "POST":
        obj.status = "fechada"
        obj.fechado_em = timezone.now()
        obj.fechado_por = request.user
        obj.save(update_fields=["status", "fechado_em", "fechado_por", "atualizado_em"])
        messages.success(request, "Folha de pagamento fechada.")
    return redirect("folha_pagamento_detail", pk=obj.pk)

