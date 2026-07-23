import io

import xhtml2pdf.pisa as pisa
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView
from django.views.generic.base import View
from reportlab.pdfgen import canvas

from .forms import FuncionarioForm
from .mixins import EmpresaAtualMixin, FuncionarioPorEmpresaMixin, PermissaoFuncionarioMixin
from .models import Funcionario
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


class FuncionarioDelete(PermissaoFuncionarioMixin, FuncionarioPorEmpresaMixin, DeleteView):
    permission_required = "funcionarios.delete_funcionario"
    model = Funcionario
    success_url = reverse_lazy("list_funcionarios")


class FuncionarioCreate(PermissaoFuncionarioMixin, EmpresaAtualMixin, CreateView):
    permission_required = "funcionarios.add_funcionario"
    model = Funcionario
    form_class = FuncionarioForm
    success_url = reverse_lazy("list_funcionarios")

    @transaction.atomic
    def form_valid(self, form):
        funcionario = form.save(commit=False)
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
