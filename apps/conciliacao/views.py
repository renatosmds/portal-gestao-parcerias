from apps.core.permissoes_modulos import exigir_modulo
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ConciliacaoForm, IgnorarMovimentacaoForm, ImportacaoExtratoForm, MovimentacaoForm, OcorrenciaForm, VinculoForm
from .models import Conciliacao, Movimentacao, OcorrenciaConciliacao, VinculoConciliacao
from .services import gerar_ocorrencias, importar_extrato


def _empresa_usuario(user):
    try:
        return user.funcionario.empresa
    except Exception:
        return None


def _qs_usuario(user):
    qs = Conciliacao.objects.select_related("prestacao", "prestacao__empresa", "criado_por")
    if user.is_staff or user.is_superuser:
        return qs
    empresa = _empresa_usuario(user)
    return qs.filter(prestacao__empresa=empresa) if empresa else qs.none()


@login_required
@exigir_modulo("conciliacao")
def painel(request):
    qs = _qs_usuario(request.user)
    contexto = {
        "conciliacoes": qs.annotate(total_mov=Count("movimentacoes"))[:100],
        "total": qs.count(),
        "fechadas": qs.filter(situacao=Conciliacao.Situacao.FECHADA).count(),
        "com_diferenca": qs.filter(situacao=Conciliacao.Situacao.COM_DIFERENCA).count(),
        "incompletas": qs.filter(situacao=Conciliacao.Situacao.INCOMPLETA).count(),
    }
    return render(request, "conciliacao/painel.html", contexto)


@login_required
@exigir_modulo("conciliacao")
def nova(request):
    if request.method == "POST":
        form = ConciliacaoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.criado_por = request.user
            obj.save()
            messages.success(request, "Conciliação criada.")
            return redirect(obj)
    else:
        form = ConciliacaoForm()
    return render(request, "conciliacao/form.html", {"form": form, "titulo": "Nova conciliação"})


@login_required
@exigir_modulo("conciliacao")
def detalhe(request, pk):
    obj = get_object_or_404(_qs_usuario(request.user), pk=pk)
    contexto = {
        "conciliacao": obj,
        "movimentacoes": obj.movimentacoes.prefetch_related("vinculos__lancamento"),
        "ocorrencias": obj.ocorrencias.all(),
        "form_importacao": ImportacaoExtratoForm(),
        "form_movimentacao": MovimentacaoForm(),
    }
    return render(request, "conciliacao/detalhe.html", contexto)


@login_required
@exigir_modulo("conciliacao")
@require_POST
def importar(request, pk):
    obj = get_object_or_404(_qs_usuario(request.user), pk=pk)
    form = ImportacaoExtratoForm(request.POST, request.FILES)
    if form.is_valid():
        imp = importar_extrato(obj, form.cleaned_data["arquivo"], request.user)
        messages.success(request, f"Extrato processado: {imp.total_importadas} movimentações importadas e {imp.total_erros} erros.")
    else:
        messages.error(request, "Não foi possível importar o extrato.")
    return redirect(obj)


@login_required
@exigir_modulo("conciliacao")
@require_POST
def adicionar_movimentacao(request, pk):
    obj = get_object_or_404(_qs_usuario(request.user), pk=pk)
    form = MovimentacaoForm(request.POST)
    if form.is_valid():
        mov = form.save(commit=False)
        mov.conciliacao = obj
        mov.save()
        gerar_ocorrencias(obj)
        messages.success(request, "Movimentação incluída.")
    else:
        messages.error(request, "Confira os dados da movimentação.")
    return redirect(obj)


@login_required
@exigir_modulo("conciliacao")
def vincular(request, mov_pk):
    mov = get_object_or_404(Movimentacao.objects.select_related("conciliacao__prestacao"), pk=mov_pk, conciliacao__in=_qs_usuario(request.user))
    if request.method == "POST":
        form = VinculoForm(request.POST, prestacao=mov.conciliacao.prestacao)
        if form.is_valid():
            vinculo = form.save(commit=False)
            vinculo.movimentacao = mov
            vinculo.confirmado_por = request.user
            vinculo.save()
            messages.success(request, "Movimentação vinculada ao lançamento.")
            return redirect(mov.conciliacao)
    else:
        form = VinculoForm(prestacao=mov.conciliacao.prestacao, initial={"valor": mov.valor_pendente})
    sugestoes = form.fields["lancamento"].queryset.filter(valor_documento=mov.valor)[:10]
    return render(request, "conciliacao/vincular.html", {"movimentacao": mov, "form": form, "sugestoes": sugestoes})


@login_required
@exigir_modulo("conciliacao")
@require_POST
def excluir_vinculo(request, pk):
    vinculo = get_object_or_404(VinculoConciliacao.objects.select_related("movimentacao__conciliacao"), pk=pk, movimentacao__conciliacao__in=_qs_usuario(request.user))
    conciliacao = vinculo.movimentacao.conciliacao
    vinculo.delete()
    messages.info(request, "Vínculo removido.")
    return redirect(conciliacao)


@login_required
@exigir_modulo("conciliacao")
@require_POST
def ignorar(request, mov_pk):
    mov = get_object_or_404(Movimentacao.objects.select_related("conciliacao"), pk=mov_pk, conciliacao__in=_qs_usuario(request.user))
    form = IgnorarMovimentacaoForm(request.POST)
    if form.is_valid():
        mov.situacao = Movimentacao.Situacao.IGNORADA
        mov.justificativa = form.cleaned_data["justificativa"]
        mov.save(update_fields=["situacao", "justificativa"])
        mov.conciliacao.recalcular_situacao()
        messages.info(request, "Movimentação ignorada mediante justificativa.")
    else:
        messages.error(request, "Informe justificativa com pelo menos 10 caracteres.")
    return redirect(mov.conciliacao)


@login_required
@exigir_modulo("conciliacao")
@require_POST
def atualizar_ocorrencia(request, pk):
    ocorrencia = get_object_or_404(OcorrenciaConciliacao.objects.select_related("conciliacao"), pk=pk, conciliacao__in=_qs_usuario(request.user))
    form = OcorrenciaForm(request.POST, instance=ocorrencia)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.atualizado_por = request.user
        obj.save()
        messages.success(request, "Ocorrência atualizada.")
    return redirect(ocorrencia.conciliacao)
