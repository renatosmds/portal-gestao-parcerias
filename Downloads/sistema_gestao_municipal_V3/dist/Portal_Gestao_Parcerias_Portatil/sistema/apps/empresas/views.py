from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import EmpresaForm
from .mixins import EmpresaEscopoMixin, EmpresaPermissaoMixin
from .models import Empresa


class EmpresaList(
    EmpresaPermissaoMixin,
    EmpresaEscopoMixin,
    ListView,
):
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

        return queryset.annotate(
            quantidade_funcionarios=Count("funcionario", distinct=True),
            quantidade_ativos=Count(
                "funcionario",
                filter=Q(funcionario__ativo=True),
                distinct=True,
            ),
            quantidade_ferias=Count(
                "funcionario",
                filter=Q(funcionario__de_ferias=True),
                distinct=True,
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["termo_busca"] = (self.request.GET.get("q") or "").strip()
        context["total_empresas"] = self.get_queryset().count()
        return context


class EmpresaDetail(
    EmpresaPermissaoMixin,
    EmpresaEscopoMixin,
    DetailView,
):
    model = Empresa
    template_name = "empresas/empresa_detail.html"
    context_object_name = "empresa"
    permission_required = "empresas.view_empresa"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        funcionarios = self.object.funcionario_set.all().order_by("nome")
        context["funcionarios"] = funcionarios[:10]
        context["total_funcionarios"] = funcionarios.count()
        context["total_ativos"] = funcionarios.filter(ativo=True).count()
        context["total_ferias"] = funcionarios.filter(de_ferias=True).count()
        return context


class EmpresaCreate(EmpresaPermissaoMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = "empresas/empresa_form.html"
    permission_required = "empresas.add_empresa"
    success_url = reverse_lazy("list_empresas")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Empresa “{self.object.nome}” cadastrada com sucesso.",
        )
        return response


class EmpresaEdit(
    EmpresaPermissaoMixin,
    EmpresaEscopoMixin,
    UpdateView,
):
    model = Empresa
    form_class = EmpresaForm
    template_name = "empresas/empresa_form.html"
    permission_required = "empresas.change_empresa"

    def get_success_url(self):
        return reverse_lazy("detail_empresa", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Empresa “{self.object.nome}” atualizada com sucesso.",
        )
        return response


class EmpresaDelete(
    EmpresaPermissaoMixin,
    EmpresaEscopoMixin,
    DeleteView,
):
    model = Empresa
    template_name = "empresas/empresa_confirm_delete.html"
    context_object_name = "empresa"
    permission_required = "empresas.delete_empresa"
    success_url = reverse_lazy("list_empresas")

    def form_valid(self, form):
        nome = self.object.nome
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Empresa “{nome}” excluída com sucesso.",
        )
        return response
