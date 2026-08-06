from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.empresas.models import Empresa
from apps.core.acesso import empresa_do_usuario, usuario_pode_ver_todas_empresas

from .forms import TermosForm
from .mixins import TermoEscopoMixin, TermoPermissaoMixin
from .models import Termos


class TermosList(TermoPermissaoMixin, TermoEscopoMixin, ListView):
    model = Termos
    template_name = "termos/termos_list.html"
    context_object_name = "termos"
    permission_required = "termos.view_termos"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        termo = (self.request.GET.get("q") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        empresa_id = (self.request.GET.get("empresa") or "").strip()

        if termo:
            queryset = queryset.filter(
                Q(termo__icontains=termo)
                | Q(numtermo__icontains=termo)
                | Q(nomeosc__icontains=termo)
                | Q(apelido__icontains=termo)
                | Q(analista__icontains=termo)
            )
        if status:
            queryset = queryset.filter(status__icontains=status)
        if empresa_id and usuario_pode_ver_todas_empresas(self.request.user):
            queryset = queryset.filter(empresa_id=empresa_id)

        return queryset.order_by("termo", "numtermo")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["termo_busca"] = (self.request.GET.get("q") or "").strip()
        context["status_filtro"] = (self.request.GET.get("status") or "").strip()
        context["empresa_filtro"] = (self.request.GET.get("empresa") or "").strip()
        context["total_termos"] = queryset.count()
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if usuario_pode_ver_todas_empresas(self.request.user)
            else Empresa.objects.none()
        )
        return context


class TermosDetail(TermoPermissaoMixin, TermoEscopoMixin, DetailView):
    model = Termos
    template_name = "termos/termo_detail.html"
    context_object_name = "termo_obj"
    permission_required = "termos.view_termos"


class TermosCreate(TermoPermissaoMixin, CreateView):
    model = Termos
    form_class = TermosForm
    template_name = "termos/termos_form.html"
    permission_required = "termos.add_termos"

    def get_empresa_destino(self):
        if usuario_pode_ver_todas_empresas(self.request.user):
            empresa_id = self.request.GET.get("empresa") or self.request.POST.get("empresa")
            return Empresa.objects.filter(pk=empresa_id).first() if empresa_id else None
        try:
            return empresa_do_usuario(self.request.user)
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
            if usuario_pode_ver_todas_empresas(self.request.user)
            else Empresa.objects.none()
        )
        return context

    def form_valid(self, form):
        empresa = self.get_empresa_destino()
        if not empresa:
            form.add_error(None, "Selecione uma empresa válida para o termo.")
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.empresa = empresa
        self.object.save()
        messages.success(self.request, f"Termo “{self.object}” cadastrado com sucesso.")
        return super().form_valid(form)


class TermosUpdate(TermoPermissaoMixin, TermoEscopoMixin, UpdateView):
    model = Termos
    form_class = TermosForm
    template_name = "termos/termos_form.html"
    permission_required = "termos.change_termos"

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
        messages.success(self.request, f"Termo “{self.object}” atualizado com sucesso.")
        return response


class TermosDelete(TermoPermissaoMixin, TermoEscopoMixin, DeleteView):
    model = Termos
    template_name = "termos/termos_confirm_delete.html"
    context_object_name = "termo_obj"
    permission_required = "termos.delete_termos"
    success_url = reverse_lazy("list_termos")
