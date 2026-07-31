from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.empresas.models import Empresa

from .forms import FornecedorForm
from .mixins import FornecedorEscopoMixin, FornecedorPermissaoMixin
from .models import Fornecedores


class FornecedoresList(
    FornecedorPermissaoMixin,
    FornecedorEscopoMixin,
    ListView,
):
    model = Fornecedores
    template_name = "fornecedores/fornecedores_list.html"
    context_object_name = "fornecedores"
    permission_required = "fornecedores.view_fornecedores"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        termo = (self.request.GET.get("q") or "").strip()
        pessoa = (self.request.GET.get("pessoa") or "").strip()
        empresa_id = (self.request.GET.get("empresa") or "").strip()

        if termo:
            queryset = queryset.filter(
                Q(credor__icontains=termo)
                | Q(razao__icontains=termo)
                | Q(fantasia__icontains=termo)
                | Q(numero__icontains=termo)
                | Q(email__icontains=termo)
            )

        if pessoa:
            queryset = queryset.filter(pessoa=pessoa)

        if empresa_id and self.request.user.is_superuser:
            queryset = queryset.filter(empresa_id=empresa_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context["termo_busca"] = (self.request.GET.get("q") or "").strip()
        context["pessoa_filtro"] = (self.request.GET.get("pessoa") or "").strip()
        context["empresa_filtro"] = (self.request.GET.get("empresa") or "").strip()
        context["total_fornecedores"] = queryset.count()
        context["total_pf"] = queryset.filter(pessoa="física").count()
        context["total_pj"] = queryset.filter(pessoa="jurídica").count()
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if self.request.user.is_superuser
            else Empresa.objects.none()
        )
        return context


class FornecedorDetail(
    FornecedorPermissaoMixin,
    FornecedorEscopoMixin,
    DetailView,
):
    model = Fornecedores
    template_name = "fornecedores/fornecedor_detail.html"
    context_object_name = "fornecedor"
    permission_required = "fornecedores.view_fornecedores"


class FornecedorCreate(
    FornecedorPermissaoMixin,
    CreateView,
):
    model = Fornecedores
    form_class = FornecedorForm
    template_name = "fornecedores/fornecedores_form.html"
    permission_required = "fornecedores.add_fornecedores"

    def get_empresa_destino(self):
        if self.request.user.is_superuser:
            empresa_id = self.request.GET.get("empresa") or self.request.POST.get("empresa")
            if empresa_id:
                return Empresa.objects.filter(pk=empresa_id).first()
            return None

        try:
            return self.request.user.funcionario.empresa
        except Exception:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa_destino()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresa_destino"] = self.get_empresa_destino()
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if self.request.user.is_superuser
            else Empresa.objects.none()
        )
        return context

    def form_valid(self, form):
        empresa = self.get_empresa_destino()

        if not empresa:
            form.add_error(
                None,
                "Selecione uma empresa válida para o fornecedor.",
            )
            return self.form_invalid(form)

        fornecedor = form.save(commit=False)
        fornecedor.empresa = empresa
        fornecedor.save()
        self.object = fornecedor

        messages.success(
            self.request,
            f"Fornecedor “{fornecedor}” cadastrado com sucesso.",
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "detail_fornecedor",
            kwargs={"pk": self.object.pk},
        )


class FornecedorUpdate(
    FornecedorPermissaoMixin,
    FornecedorEscopoMixin,
    UpdateView,
):
    model = Fornecedores
    form_class = FornecedorForm
    template_name = "fornecedores/fornecedores_form.html"
    permission_required = "fornecedores.change_fornecedores"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.object.empresa
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresa_destino"] = self.object.empresa
        context["empresas_disponiveis"] = Empresa.objects.none()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Fornecedor “{self.object}” atualizado com sucesso.",
        )
        return response

    def get_success_url(self):
        return reverse_lazy(
            "detail_fornecedor",
            kwargs={"pk": self.object.pk},
        )


class FornecedorDelete(
    FornecedorPermissaoMixin,
    FornecedorEscopoMixin,
    DeleteView,
):
    model = Fornecedores
    template_name = "fornecedores/fornecedores_confirm_delete.html"
    context_object_name = "fornecedor"
    permission_required = "fornecedores.delete_fornecedores"
    success_url = reverse_lazy("list_fornecedores")

    def form_valid(self, form):
        nome = str(self.object)
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Fornecedor “{nome}” excluído com sucesso.",
        )
        return response
