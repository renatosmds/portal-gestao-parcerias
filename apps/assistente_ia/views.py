from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from apps.documentos.models import Documento

from .forms import RevisaoProcessamentoForm
from .models import AchadoAssistido, ProcessamentoAssistido
from .services import gerar_rascunhos, validar_documento


def _empresa_usuario(user):
    if user.is_superuser or user.is_staff:
        return None
    try:
        return user.funcionario.empresa
    except Exception:
        return None


def _documentos_no_escopo(user):
    qs = Documento.objects.select_related(
        "empresa", "termo", "prestacao", "lancamento"
    )
    empresa = _empresa_usuario(user)
    if user.is_superuser or user.is_staff:
        return qs
    if empresa:
        return qs.filter(empresa=empresa)
    return qs.none()


def _processamentos_no_escopo(user):
    qs = ProcessamentoAssistido.objects.select_related(
        "documento", "empresa", "solicitado_por", "revisado_por"
    ).prefetch_related("achados")
    empresa = _empresa_usuario(user)
    if user.is_superuser or user.is_staff:
        return qs
    if empresa:
        return qs.filter(empresa=empresa)
    return qs.none()


class CentralAssistenteIA(LoginRequiredMixin, ListView):
    template_name = "assistente_ia/central.html"
    context_object_name = "documentos"
    paginate_by = 20

    def get_queryset(self):
        qs = _documentos_no_escopo(self.request.user).annotate(
            total_processamentos=Count("processamentos_assistidos")
        )
        termo = self.request.GET.get("termo", "").strip()
        busca = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "").strip()
        if termo:
            qs = qs.filter(termo_id=termo)
        if status:
            qs = qs.filter(status=status)
        if busca:
            qs = qs.filter(
                Q(descricao__icontains=busca)
                | Q(numero_documento__icontains=busca)
                | Q(empresa__nome__icontains=busca)
            )
        return qs.order_by("-atualizado_em", "-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        processamentos = _processamentos_no_escopo(self.request.user)
        context.update(
            {
                "total_documentos": _documentos_no_escopo(self.request.user).count(),
                "total_processamentos": processamentos.count(),
                "aguardando_revisao": processamentos.filter(
                    decisao_revisor=ProcessamentoAssistido.DecisaoRevisor.PENDENTE
                ).count(),
                "ia_externa_ativa": bool(settings.PGP_IA_ATIVA and settings.OPENAI_API_KEY),
                "processamentos_recentes": processamentos[:8],
            }
        )
        return context


class ExecutarAnaliseLocal(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, pk):
        documento = get_object_or_404(_documentos_no_escopo(request.user), pk=pk)
        achados = validar_documento(documento)
        rascunhos = gerar_rascunhos(documento, achados)
        processamento = ProcessamentoAssistido.objects.create(
            documento=documento,
            empresa=documento.empresa,
            solicitado_por=request.user,
            resumo=rascunhos["resumo"],
            rascunho_inconformidade=rascunhos["inconformidade"],
            rascunho_diligencia=rascunhos["diligencia"],
            rascunho_recomendacao=rascunhos["recomendacao"],
            ia_externa_utilizada=False,
        )
        AchadoAssistido.objects.bulk_create(
            [
                AchadoAssistido(
                    processamento=processamento,
                    codigo=achado["codigo"],
                    severidade=achado["severidade"],
                    titulo=achado["titulo"],
                    descricao=achado["descricao"],
                    ordem=ordem,
                )
                for ordem, achado in enumerate(achados, start=1)
            ]
        )
        messages.success(
            request,
            "Análise local concluída. Revise os achados antes de utilizá-los.",
        )
        return redirect(processamento.get_absolute_url())


class ProcessamentoDetalhe(LoginRequiredMixin, DetailView):
    model = ProcessamentoAssistido
    template_name = "assistente_ia/detalhe.html"
    context_object_name = "processamento"

    def get_queryset(self):
        return _processamentos_no_escopo(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_revisao"] = RevisaoProcessamentoForm(instance=self.object)
        return context


class RevisarProcessamento(LoginRequiredMixin, View):
    def post(self, request, pk):
        processamento = get_object_or_404(
            _processamentos_no_escopo(request.user), pk=pk
        )
        form = RevisaoProcessamentoForm(request.POST, instance=processamento)
        if form.is_valid():
            processamento = form.save(commit=False)
            processamento.revisado_por = request.user
            processamento.revisado_em = timezone.now()
            processamento.status = ProcessamentoAssistido.Status.REVISADO
            processamento.save()
            messages.success(request, "Revisão humana registrada com sucesso.")
        else:
            messages.error(request, "Não foi possível registrar a revisão.")
        return redirect(reverse("assistente_ia_detalhe", kwargs={"pk": pk}))
