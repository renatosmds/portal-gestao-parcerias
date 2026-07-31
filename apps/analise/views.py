from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.empresas.models import Empresa

from .forms import AnaliseForm
from .mixins import AnaliseEscopoMixin, AnalisePermissaoMixin
from .models import Analise


class AnaliseList(AnalisePermissaoMixin, AnaliseEscopoMixin, ListView):
    model = Analise
    template_name = "analise/analise_list.html"
    context_object_name = "analises"
    permission_required = "analise.view_analise"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        termo = (self.request.GET.get("q") or "").strip()
        situacao = (self.request.GET.get("situacao") or "").strip()
        empresa_id = (self.request.GET.get("empresa") or "").strip()

        if termo:
            queryset = queryset.filter(
                Q(numtermo__termo__icontains=termo)
                | Q(numtermo__numtermo__icontains=termo)
                | Q(prestacao__numtermo__icontains=termo)
                | Q(nomeOSC__icontains=termo)
                | Q(numRA__icontains=termo)
                | Q(item__icontains=termo)
                | Q(inconformidade__icontains=termo)
                | Q(recomendacoes__icontains=termo)
                | Q(status__icontains=termo)
            )

        if situacao == "concluida":
            queryset = queryset.filter(concluida=True)
        elif situacao == "andamento":
            queryset = queryset.filter(concluida=False)

        if empresa_id and self.request.user.is_superuser:
            queryset = queryset.filter(empresa_id=empresa_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["termo_busca"] = (self.request.GET.get("q") or "").strip()
        context["situacao_filtro"] = (
            self.request.GET.get("situacao") or ""
        ).strip()
        context["empresa_filtro"] = (
            self.request.GET.get("empresa") or ""
        ).strip()
        context["total_analises"] = queryset.count()
        context["total_andamento"] = queryset.filter(concluida=False).count()
        context["total_concluidas"] = queryset.filter(concluida=True).count()
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if self.request.user.is_superuser
            else Empresa.objects.none()
        )
        return context


class AnaliseDetail(AnalisePermissaoMixin, AnaliseEscopoMixin, DetailView):
    model = Analise
    template_name = "analise/analise_detail.html"
    context_object_name = "analise"
    permission_required = "analise.view_analise"


class AnaliseCreate(AnalisePermissaoMixin, CreateView):
    model = Analise
    form_class = AnaliseForm
    template_name = "analise/analise_form.html"
    permission_required = "analise.add_analise"

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
                "Selecione uma empresa válida para a análise.",
            )
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.empresa = empresa

        if self.object.numtermo_id and not self.object.nomeOSC:
            self.object.nomeOSC = self.object.numtermo.nomeosc

        self.object.save()

        messages.success(
            self.request,
            f"Análise “{self.object}” cadastrada com sucesso.",
        )
        return super().form_valid(form)


class AnaliseUpdate(
    AnalisePermissaoMixin,
    AnaliseEscopoMixin,
    UpdateView,
):
    model = Analise
    form_class = AnaliseForm
    template_name = "analise/analise_form.html"
    permission_required = "analise.change_analise"

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
            f"Análise “{self.object}” atualizada com sucesso.",
        )
        return response


class AnaliseDelete(
    AnalisePermissaoMixin,
    AnaliseEscopoMixin,
    DeleteView,
):
    model = Analise
    template_name = "analise/analise_confirm_delete.html"
    context_object_name = "analise"
    permission_required = "analise.delete_analise"
    success_url = reverse_lazy("list_analise")
