from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.empresas.models import Empresa
from apps.core.acesso import empresa_do_usuario, filtrar_por_empresa, usuario_pode_ver_todas_empresas

from .forms import MovimentarPrestacaoForm, PrestacaoForm
from .mixins import PrestacaoEscopoMixin, PrestacaoPermissaoMixin
from .models import HistoricoPrestacao, Prestacao


class PrestacaoList(PrestacaoPermissaoMixin, PrestacaoEscopoMixin, ListView):
    model = Prestacao
    template_name = "prestacao/prestacao_list.html"
    context_object_name = "prestacoes"
    permission_required = "prestacao.view_prestacao"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        termo = (self.request.GET.get("q") or "").strip()
        situacao = (self.request.GET.get("situacao") or "").strip()
        empresa_id = (self.request.GET.get("empresa") or "").strip()

        if termo:
            queryset = queryset.filter(
                Q(numtermo__icontains=termo)
                | Q(credor__icontains=termo)
                | Q(CpfCnpj__icontains=termo)
                | Q(gestora__icontains=termo)
                | Q(matricula__icontains=termo)
            )

        if situacao == "concluida":
            queryset = queryset.filter(concluida=True)
        elif situacao == "andamento":
            queryset = queryset.filter(concluida=False)

        if empresa_id and usuario_pode_ver_todas_empresas(self.request.user):
            queryset = queryset.filter(empresa_id=empresa_id)

        return queryset.order_by("concluida", "numtermo", "credor")

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
        context["total_prestacoes"] = queryset.count()
        context["total_andamento"] = queryset.filter(concluida=False).count()
        context["total_concluidas"] = queryset.filter(concluida=True).count()
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if usuario_pode_ver_todas_empresas(self.request.user)
            else Empresa.objects.none()
        )
        return context


class PrestacaoDetail(PrestacaoPermissaoMixin, PrestacaoEscopoMixin, DetailView):
    model = Prestacao
    template_name = "prestacao/prestacao_detail.html"
    context_object_name = "prestacao"
    permission_required = "prestacao.view_prestacao"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["historico"] = self.object.historico_workflow.select_related("usuario")[:20]
        context["total_lancamentos"] = self.object.lancamentos.count()
        context["total_glosado"] = sum((x.valor_glosa for x in self.object.lancamentos.all()), 0)
        return context


class PrestacaoCreate(PrestacaoPermissaoMixin, CreateView):
    model = Prestacao
    form_class = PrestacaoForm
    template_name = "prestacao/prestacao_form.html"
    permission_required = "prestacao.add_prestacao"

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
            form.add_error(
                None,
                "Selecione uma empresa válida para a prestação.",
            )
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.empresa = empresa
        self.object.save()

        messages.success(
            self.request,
            f"Prestação “{self.object}” cadastrada com sucesso.",
        )
        return super().form_valid(form)


class PrestacaoEdit(
    PrestacaoPermissaoMixin,
    PrestacaoEscopoMixin,
    UpdateView,
):
    model = Prestacao
    form_class = PrestacaoForm
    template_name = "prestacao/prestacao_form.html"
    permission_required = "prestacao.change_prestacao"

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
            f"Prestação “{self.object}” atualizada com sucesso.",
        )
        return response


class PrestacaoDelete(
    PrestacaoPermissaoMixin,
    PrestacaoEscopoMixin,
    DeleteView,
):
    model = Prestacao
    template_name = "prestacao/prestacao_confirm_delete.html"
    context_object_name = "prestacao"
    permission_required = "prestacao.delete_prestacao"
    success_url = reverse_lazy("list_prestacao")


TRANSICOES = {
    "elaboracao": {"enviada"}, "enviada": {"recebida"}, "recebida": {"em_analise"},
    "em_analise": {"diligencia", "aprovada", "aprovada_ressalvas", "reprovada"},
    "diligencia": {"corrigida"}, "corrigida": {"em_analise"},
    "aprovada": {"encerrada"}, "aprovada_ressalvas": {"encerrada"}, "reprovada": {"encerrada"},
}

@login_required
@permission_required("prestacao.change_prestacao", raise_exception=True)
def movimentar_prestacao(request, pk):
    prestacao = get_object_or_404(filtrar_por_empresa(Prestacao.objects.all(), request.user), pk=pk)
    permitidas = TRANSICOES.get(prestacao.situacao_workflow, set())
    form = MovimentarPrestacaoForm(request.POST or None, situacoes_permitidas=permitidas)
    if request.method == "POST" and form.is_valid():
        anterior = prestacao.situacao_workflow
        nova = form.cleaned_data["nova_situacao"]
        if nova not in permitidas:
            form.add_error("nova_situacao", "Transição não permitida para a situação atual.")
        else:
            prestacao.situacao_workflow = nova
            if nova == Prestacao.SituacaoWorkflow.ENVIADA: prestacao.enviada_em = timezone.now()
            if nova == Prestacao.SituacaoWorkflow.RECEBIDA: prestacao.recebida_em = timezone.now()
            if nova == Prestacao.SituacaoWorkflow.ENCERRADA: prestacao.concluida = True
            prestacao.save()
            HistoricoPrestacao.objects.create(prestacao=prestacao, situacao_anterior=anterior, nova_situacao=nova, observacao=form.cleaned_data["observacao"], usuario=request.user)
            messages.success(request, "Movimentação registrada no histórico da prestação.")
            return redirect("detail_prestacao", pk=prestacao.pk)
    return render(request, "prestacao/prestacao_movimentar.html", {"prestacao":prestacao, "form":form})
