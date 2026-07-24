from django.contrib import messages
from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.empresas.models import Empresa

from .forms import LancamentoForm
from .mixins import LancamentoEscopoMixin, LancamentoPermissaoMixin
from .models import Lancamento


class LancamentoList(
    LancamentoPermissaoMixin,
    LancamentoEscopoMixin,
    ListView,
):
    model = Lancamento
    template_name = "lancamentos/lancamento_list.html"
    context_object_name = "lancamentos"
    permission_required = "lancamentos.view_lancamento"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = (self.request.GET.get("q") or "").strip()
        situacao = (self.request.GET.get("situacao") or "").strip()
        empresa_id = (self.request.GET.get("empresa") or "").strip()

        if busca:
            queryset = queryset.filter(
                Q(numero_lancamento__icontains=busca)
                | Q(numero_documento__icontains=busca)
                | Q(chave_acesso__icontains=busca)
                | Q(descricao__icontains=busca)
                | Q(fornecedor__credor__icontains=busca)
                | Q(fornecedor__razao__icontains=busca)
                | Q(fornecedor__fantasia__icontains=busca)
                | Q(termo__termo__icontains=busca)
                | Q(termo__numtermo__icontains=busca)
                | Q(prestacao__numtermo__icontains=busca)
            )

        if situacao:
            queryset = queryset.filter(situacao=situacao)

        if empresa_id and self.request.user.is_superuser:
            queryset = queryset.filter(empresa_id=empresa_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        totais = queryset.aggregate(
            total_documentos=Coalesce(
                Sum("valor_documento"),
                Value(0),
                output_field=DecimalField(max_digits=15, decimal_places=2),
            ),
            total_glosas=Coalesce(
                Sum("valor_glosa"),
                Value(0),
                output_field=DecimalField(max_digits=15, decimal_places=2),
            ),
        )
        context.update(totais)
        context["total_lancamentos"] = queryset.count()
        context["busca"] = (self.request.GET.get("q") or "").strip()
        context["situacao_filtro"] = (
            self.request.GET.get("situacao") or ""
        ).strip()
        context["empresa_filtro"] = (
            self.request.GET.get("empresa") or ""
        ).strip()
        context["situacoes"] = Lancamento.Situacao.choices
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if self.request.user.is_superuser
            else Empresa.objects.none()
        )
        return context


class LancamentoDetail(
    LancamentoPermissaoMixin,
    LancamentoEscopoMixin,
    DetailView,
):
    model = Lancamento
    template_name = "lancamentos/lancamento_detail.html"
    context_object_name = "lancamento"
    permission_required = "lancamentos.view_lancamento"


class LancamentoCreate(LancamentoPermissaoMixin, CreateView):
    model = Lancamento
    form_class = LancamentoForm
    template_name = "lancamentos/lancamento_form.html"
    permission_required = "lancamentos.add_lancamento"

    def get_empresa_destino(self):
        if self.request.user.is_superuser:
            empresa_id = (
                self.request.GET.get("empresa")
                or self.request.POST.get("empresa")
            )
            return (
                Empresa.objects.filter(pk=empresa_id).first()
                if empresa_id
                else None
            )
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
                "Selecione uma empresa válida para o lançamento.",
            )
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.empresa = empresa
        self.object.criado_por = self.request.user
        self.object.save()

        messages.success(
            self.request,
            f"Lançamento “{self.object}” cadastrado com sucesso.",
        )
        return super().form_valid(form)


class LancamentoUpdate(
    LancamentoPermissaoMixin,
    LancamentoEscopoMixin,
    UpdateView,
):
    model = Lancamento
    form_class = LancamentoForm
    template_name = "lancamentos/lancamento_form.html"
    permission_required = "lancamentos.change_lancamento"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.object.empresa
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Lançamento “{self.object}” atualizado com sucesso.",
        )
        return response


class LancamentoDelete(
    LancamentoPermissaoMixin,
    LancamentoEscopoMixin,
    DeleteView,
):
    model = Lancamento
    template_name = "lancamentos/lancamento_confirm_delete.html"
    context_object_name = "lancamento"
    permission_required = "lancamentos.delete_lancamento"
    success_url = reverse_lazy("list_lancamentos")
