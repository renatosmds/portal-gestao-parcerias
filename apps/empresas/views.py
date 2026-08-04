from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import EmpresaForm
from .mixins import EmpresaEscopoMixin, EmpresaPermissaoMixin
from .models import Empresa


class EmpresaList(EmpresaPermissaoMixin, EmpresaEscopoMixin, ListView):
    model = Empresa
    template_name = "empresas/empresa_list.html"
    context_object_name = "empresas"
    permission_required = "empresas.view_empresa"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        termo = (self.request.GET.get("q") or "").strip()
        if termo:
            queryset = queryset.filter(nome__icontains=termo)

        # Evita falhas de agregação em bancos legados e mantém os indicadores.
        for empresa in queryset:
            funcionarios = empresa.funcionario_set.all()
            empresa.quantidade_funcionarios = funcionarios.count()
            empresa.quantidade_ativos = funcionarios.filter(ativo=True).count()
            empresa.quantidade_ferias = funcionarios.filter(de_ferias=True).count()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["termo_busca"] = (self.request.GET.get("q") or "").strip()
        context["total_empresas"] = self.get_queryset().count()
        return context


class EmpresaDetail(EmpresaPermissaoMixin, EmpresaEscopoMixin, DetailView):
    model = Empresa
    template_name = "empresas/empresa_detail.html"
    context_object_name = "empresa"
    permission_required = "empresas.view_empresa"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        funcionarios = self.object.funcionario_set.all().order_by("nome")
        context.update({
            "funcionarios": funcionarios[:10],
            "total_funcionarios": funcionarios.count(),
            "total_ativos": funcionarios.filter(ativo=True).count(),
            "total_ferias": funcionarios.filter(de_ferias=True).count(),
        })
        return context


class EmpresaCreate(EmpresaPermissaoMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = "empresas/empresa_form.html"
    permission_required = "empresas.add_empresa"
    success_url = reverse_lazy("list_empresas")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Empresa ‘{self.object.nome}’ cadastrada com sucesso.")
        return response


class EmpresaEdit(EmpresaPermissaoMixin, EmpresaEscopoMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = "empresas/empresa_form.html"
    permission_required = "empresas.change_empresa"

    def get_success_url(self):
        return reverse_lazy("detail_empresa", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Empresa ‘{self.object.nome}’ atualizada com sucesso.")
        return response


class EmpresaDelete(EmpresaPermissaoMixin, EmpresaEscopoMixin, DeleteView):
    model = Empresa
    template_name = "empresas/empresa_confirm_delete.html"
    context_object_name = "empresa"
    permission_required = "empresas.delete_empresa"
    success_url = reverse_lazy("list_empresas")
