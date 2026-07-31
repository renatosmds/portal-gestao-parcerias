from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.empresas.models import Empresa

from .forms import ParceriasForm
from .mixins import ParceriaEscopoMixin, ParceriaPermissaoMixin
from .models import Parcerias


class ParceriasList(
    ParceriaPermissaoMixin,
    ParceriaEscopoMixin,
    ListView,
):
    model = Parcerias
    template_name = "parcerias/parcerias_list.html"
    context_object_name = "parcerias"
    permission_required = "parcerias.view_parcerias"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        termo = (self.request.GET.get("q") or "").strip()
        situacao = (self.request.GET.get("situacao") or "").strip()
        empresa_id = (self.request.GET.get("empresa") or "").strip()

        if termo:
            queryset = queryset.filter(
                Q(nomeOSC__icontains=termo)
                | Q(numtermo__termo__icontains=termo)
                | Q(numtermo__numtermo__icontains=termo)
                | Q(credor__credor__icontains=termo)
                | Q(status__icontains=termo)
            )

        if situacao == "concluida":
            queryset = queryset.filter(concluido=True)
        elif situacao == "andamento":
            queryset = queryset.filter(concluido=False)

        if empresa_id and self.request.user.is_superuser:
            queryset = queryset.filter(empresa_id=empresa_id)

        return queryset.order_by("concluido", "numtermo__termo", "nomeOSC")

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
        context["total_parcerias"] = queryset.count()
        context["total_andamento"] = queryset.filter(concluido=False).count()
        context["total_concluidas"] = queryset.filter(concluido=True).count()
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if self.request.user.is_superuser
            else Empresa.objects.none()
        )
        return context


class ParceriaDetail(
    ParceriaPermissaoMixin,
    ParceriaEscopoMixin,
    DetailView,
):
    model = Parcerias
    template_name = "parcerias/parceria_detail.html"
    context_object_name = "parceria"
    permission_required = "parcerias.view_parcerias"


class ParceriaCreate(
    ParceriaPermissaoMixin,
    CreateView,
):
    model = Parcerias
    form_class = ParceriasForm
    template_name = "parcerias/parcerias_form.html"
    permission_required = "parcerias.add_parcerias"

    def get_empresa_destino(self):
        if self.request.user.is_superuser:
            empresa_id = (
                self.request.GET.get("empresa")
                or self.request.POST.get("empresa")
            )
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
                "Selecione uma empresa válida para a parceria.",
            )
            return self.form_invalid(form)

        parceria = form.save(commit=False)
        parceria.empresa = empresa
        parceria.save()
        self.object = parceria

        messages.success(
            self.request,
            f"Parceria “{parceria}” cadastrada com sucesso.",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "detail_parceria",
            kwargs={"pk": self.object.pk},
        )


class ParceriaUpdate(
    ParceriaPermissaoMixin,
    ParceriaEscopoMixin,
    UpdateView,
):
    model = Parcerias
    form_class = ParceriasForm
    template_name = "parcerias/parcerias_form.html"
    permission_required = "parcerias.change_parcerias"

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
            f"Parceria “{self.object}” atualizada com sucesso.",
        )
        return response

    def get_success_url(self):
        return reverse_lazy(
            "detail_parceria",
            kwargs={"pk": self.object.pk},
        )


class ParceriaDelete(
    ParceriaPermissaoMixin,
    ParceriaEscopoMixin,
    DeleteView,
):
    model = Parcerias
    template_name = "parcerias/parcerias_confirm_delete.html"
    context_object_name = "parceria"
    permission_required = "parcerias.delete_parcerias"
    success_url = reverse_lazy("list_parcerias")

    def form_valid(self, form):
        nome = str(self.object)
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Parceria “{nome}” excluída com sucesso.",
        )
        return response
