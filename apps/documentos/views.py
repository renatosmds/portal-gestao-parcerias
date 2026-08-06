from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.empresas.models import Empresa
from apps.core.acesso import empresa_do_usuario, usuario_pode_ver_todas_empresas

from .forms import ConferenciaDocumentoForm, DocumentoForm
from .mixins import DocumentoEscopoMixin, DocumentoPermissaoMixin
from .models import Documento


class DocumentoList(
    DocumentoPermissaoMixin,
    DocumentoEscopoMixin,
    ListView,
):
    model = Documento
    template_name = "documentos/documento_list.html"
    context_object_name = "documentos"
    permission_required = "documentos.view_documento"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = (self.request.GET.get("q") or "").strip()
        status = (self.request.GET.get("status") or "").strip()
        tipo = (self.request.GET.get("tipo") or "").strip()
        empresa_id = (self.request.GET.get("empresa") or "").strip()

        if busca:
            queryset = queryset.filter(
                Q(descricao__icontains=busca)
                | Q(numero_documento__icontains=busca)
                | Q(termo__termo__icontains=busca)
                | Q(termo__numtermo__icontains=busca)
                | Q(prestacao__numtermo__icontains=busca)
                | Q(lancamento__numero_lancamento__icontains=busca)
            )

        if status:
            queryset = queryset.filter(status=status)

        if tipo:
            queryset = queryset.filter(tipo=tipo)

        if empresa_id and usuario_pode_ver_todas_empresas(self.request.user):
            queryset = queryset.filter(empresa_id=empresa_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["busca"] = (self.request.GET.get("q") or "").strip()
        context["status_filtro"] = (
            self.request.GET.get("status") or ""
        ).strip()
        context["tipo_filtro"] = (
            self.request.GET.get("tipo") or ""
        ).strip()
        context["empresa_filtro"] = (
            self.request.GET.get("empresa") or ""
        ).strip()
        context["status_opcoes"] = Documento.Status.choices
        context["tipo_opcoes"] = Documento.Tipo.choices
        context["total_documentos"] = queryset.count()
        context["total_pendentes"] = queryset.filter(
            status=Documento.Status.PENDENTE
        ).count()
        context["total_pendencias"] = queryset.filter(
            status=Documento.Status.COM_PENDENCIA
        ).count()
        context["total_conferidos"] = queryset.filter(
            status=Documento.Status.CONFERIDO
        ).count()
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if usuario_pode_ver_todas_empresas(self.request.user)
            else Empresa.objects.none()
        )
        return context


class DocumentoDetail(
    DocumentoPermissaoMixin,
    DocumentoEscopoMixin,
    DetailView,
):
    model = Documento
    template_name = "documentos/documento_detail.html"
    context_object_name = "documento"
    permission_required = "documentos.view_documento"


class DocumentoCreate(DocumentoPermissaoMixin, CreateView):
    model = Documento
    form_class = DocumentoForm
    template_name = "documentos/documento_form.html"
    permission_required = "documentos.add_documento"

    def get_empresa_destino(self):
        if usuario_pode_ver_todas_empresas(self.request.user):
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
            return empresa_do_usuario(self.request.user)
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
            if usuario_pode_ver_todas_empresas(self.request.user)
            else Empresa.objects.none()
        )
        return context

    def form_valid(self, form):
        empresa = self.get_empresa_destino()
        if not empresa:
            form.add_error(
                None,
                "Selecione uma empresa válida para o documento.",
            )
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.empresa = empresa
        self.object.save()

        messages.success(
            self.request,
            f"Documento “{self.object}” cadastrado com sucesso.",
        )
        return super().form_valid(form)


class DocumentoUpdate(
    DocumentoPermissaoMixin,
    DocumentoEscopoMixin,
    UpdateView,
):
    model = Documento
    form_class = DocumentoForm
    template_name = "documentos/documento_form.html"
    permission_required = "documentos.change_documento"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.object.empresa
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Documento “{self.object}” atualizado com sucesso.",
        )
        return response


class DocumentoConferencia(
    DocumentoPermissaoMixin,
    DocumentoEscopoMixin,
    UpdateView,
):
    model = Documento
    form_class = ConferenciaDocumentoForm
    template_name = "documentos/documento_conferencia.html"
    context_object_name = "documento"
    permission_required = "documentos.change_documento"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.conferido_por = self.request.user

        if self.object.status in {
            Documento.Status.CONFERIDO,
            Documento.Status.COM_PENDENCIA,
            Documento.Status.REPROVADO,
        }:
            self.object.conferido_em = timezone.now()
        else:
            self.object.conferido_em = None

        self.object.save()

        messages.success(
            self.request,
            f"Conferência do documento “{self.object}” atualizada.",
        )
        return super().form_valid(form)


class DocumentoDelete(
    DocumentoPermissaoMixin,
    DocumentoEscopoMixin,
    DeleteView,
):
    model = Documento
    template_name = "documentos/documento_confirm_delete.html"
    context_object_name = "documento"
    permission_required = "documentos.delete_documento"
    success_url = reverse_lazy("list_documentos")
