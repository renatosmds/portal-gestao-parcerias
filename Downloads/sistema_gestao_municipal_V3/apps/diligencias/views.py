from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.core.dashboard import empresa_do_usuario, usuario_eh_osc
from .forms import ComentarioInternoForm, DiligenciaForm, RespostaDiligenciaForm
from .models import ComentarioInterno, Diligencia, Notificacao, RespostaDiligencia


def _qs_usuario(user):
    qs = Diligencia.objects.select_related("empresa", "prestacao", "lancamento", "documento", "funcionario", "responsavel", "criada_por")
    if user.is_superuser or not usuario_eh_osc(user):
        return qs
    empresa = empresa_do_usuario(user)
    return qs.filter(empresa=empresa) if empresa else qs.none()


class DiligenciaList(LoginRequiredMixin, ListView):
    model = Diligencia
    template_name = "diligencias/diligencia_list.html"
    context_object_name = "diligencias"
    paginate_by = 25

    def get_queryset(self):
        qs = _qs_usuario(self.request.user)
        status = self.request.GET.get("status")
        termo = self.request.GET.get("q", "").strip()
        if status:
            qs = qs.filter(status=status)
        if termo:
            qs = qs.filter(Q(assunto__icontains=termo) | Q(descricao__icontains=termo))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Diligencia.Status.choices
        ctx["hoje"] = timezone.localdate()
        return ctx


class DiligenciaDetail(LoginRequiredMixin, DetailView):
    model = Diligencia
    template_name = "diligencias/diligencia_detail.html"
    context_object_name = "diligencia"

    def get_queryset(self):
        return _qs_usuario(self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if usuario_eh_osc(self.request.user) and obj.status == Diligencia.Status.ENVIADA:
            obj.status = Diligencia.Status.VISUALIZADA
            obj.visualizada_em = timezone.now()
            obj.save(update_fields=["status", "visualizada_em", "atualizado_em"])
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["resposta_form"] = RespostaDiligenciaForm()
        ctx["comentario_form"] = ComentarioInternoForm()
        ctx["usuario_osc"] = usuario_eh_osc(self.request.user)
        return ctx


class DiligenciaCreate(LoginRequiredMixin, CreateView):
    model = Diligencia
    form_class = DiligenciaForm
    template_name = "diligencias/diligencia_form.html"

    def dispatch(self, request, *args, **kwargs):
        if usuario_eh_osc(request.user) and not request.user.is_superuser:
            messages.error(request, "A criação de diligências é exclusiva do órgão público.")
            return redirect("list_diligencias")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.criada_por = self.request.user
        return super().form_valid(form)


class DiligenciaUpdate(LoginRequiredMixin, UpdateView):
    model = Diligencia
    form_class = DiligenciaForm
    template_name = "diligencias/diligencia_form.html"

    def dispatch(self, request, *args, **kwargs):
        if usuario_eh_osc(request.user) and not request.user.is_superuser:
            messages.error(request, "A edição da diligência é exclusiva do órgão público.")
            return redirect("list_diligencias")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return _qs_usuario(self.request.user)


@login_required
@require_POST
def enviar_diligencia(request, pk):
    d = get_object_or_404(_qs_usuario(request.user), pk=pk)
    if usuario_eh_osc(request.user) and not request.user.is_superuser:
        messages.error(request, "Operação exclusiva do órgão público.")
        return redirect(d)
    d.status = Diligencia.Status.ENVIADA
    d.enviada_em = timezone.now()
    d.save(update_fields=["status", "enviada_em", "atualizado_em"])
    if d.empresa:
        usuarios = [f.user for f in d.empresa.funcionario_set.select_related("user").all() if f.user_id]
        Notificacao.objects.bulk_create([Notificacao(usuario=u, diligencia=d, titulo="Nova diligência", mensagem=d.assunto) for u in usuarios])
    messages.success(request, "Diligência enviada à OSC.")
    return redirect(d)


@login_required
def responder_diligencia(request, pk):
    d = get_object_or_404(_qs_usuario(request.user), pk=pk)
    if request.method != "POST":
        return redirect(d)
    form = RespostaDiligenciaForm(request.POST, request.FILES)
    if form.is_valid():
        resposta = form.save(commit=False)
        resposta.diligencia = d
        resposta.criada_por = request.user
        resposta.save()
        d.status = Diligencia.Status.RESPONDIDA
        d.save(update_fields=["status", "atualizado_em"])
        if d.responsavel:
            Notificacao.objects.create(usuario=d.responsavel, diligencia=d, titulo="Diligência respondida", mensagem=d.assunto)
        messages.success(request, "Resposta registrada.")
    else:
        messages.error(request, "Revise os dados da resposta.")
    return redirect(d)


@login_required
def comentar_interno(request, pk):
    d = get_object_or_404(_qs_usuario(request.user), pk=pk)
    if usuario_eh_osc(request.user) and not request.user.is_superuser:
        messages.error(request, "Comentários internos são exclusivos do órgão público.")
        return redirect(d)
    form = ComentarioInternoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.diligencia = d
        obj.criado_por = request.user
        obj.save()
        messages.success(request, "Comentário interno registrado.")
    return redirect(d)


@login_required
@require_POST
def alterar_status(request, pk, status):
    d = get_object_or_404(_qs_usuario(request.user), pk=pk)
    permitidos = dict(Diligencia.Status.choices)
    if status not in permitidos:
        messages.error(request, "Situação inválida.")
        return redirect(d)
    if usuario_eh_osc(request.user) and status not in {Diligencia.Status.EM_RESPOSTA, Diligencia.Status.RESPONDIDA}:
        messages.error(request, "Esta movimentação é exclusiva do órgão público.")
        return redirect(d)
    d.status = status
    if status in {Diligencia.Status.ATENDIDA, Diligencia.Status.NAO_ATENDIDA, Diligencia.Status.CANCELADA}:
        d.encerrada_em = timezone.now()
    d.save(update_fields=["status", "encerrada_em", "atualizado_em"])
    messages.success(request, f"Situação alterada para {permitidos[status]}.")
    return redirect(d)


@login_required
def notificacoes(request):
    itens = request.user.notificacoes_pgp.select_related("diligencia")[:50]
    return render(request, "diligencias/notificacoes.html", {"notificacoes": itens})


@login_required
def marcar_notificacao_lida(request, pk):
    item = get_object_or_404(request.user.notificacoes_pgp, pk=pk)
    item.lida = True
    item.save(update_fields=["lida"])
    return redirect(item.diligencia or "notificacoes")
