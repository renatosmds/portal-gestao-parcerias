from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MetaExecucaoForm
from .models import AtualizacaoMeta, MetaExecucao


def _empresa_usuario(user):
    try:
        return user.funcionario.empresa
    except Exception:
        return None


def _qs_usuario(user):
    qs = MetaExecucao.objects.select_related("prestacao", "prestacao__empresa")
    if user.is_staff or user.is_superuser:
        return qs
    empresa = _empresa_usuario(user)
    return qs.filter(prestacao__empresa=empresa) if empresa else qs.none()


@login_required
def painel(request):
    qs = _qs_usuario(request.user)
    termo = request.GET.get("q", "").strip()
    situacao = request.GET.get("situacao", "")
    if termo:
        qs = qs.filter(Q(titulo__icontains=termo) | Q(codigo__icontains=termo) | Q(prestacao__numtermo__icontains=termo))
    if situacao:
        qs = qs.filter(situacao=situacao)
    contexto = {
        "metas": qs[:200],
        "total": qs.count(),
        "atingidas": qs.filter(situacao=MetaExecucao.Situacao.ATINGIDA).count(),
        "andamento": qs.filter(situacao=MetaExecucao.Situacao.EM_ANDAMENTO).count(),
        "criticas": qs.filter(situacao__in=[MetaExecucao.Situacao.PARCIAL, MetaExecucao.Situacao.NAO_ATINGIDA]).count(),
        "situacoes": MetaExecucao.Situacao.choices,
        "q": termo,
        "situacao_atual": situacao,
    }
    return render(request, "metas/painel.html", contexto)


@login_required
def nova(request):
    form = MetaExecucaoForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.criado_por = request.user
        obj.atualizado_por = request.user
        obj.save()
        AtualizacaoMeta.objects.create(meta=obj, valor_realizado=obj.valor_realizado, situacao=obj.situacao, observacao="Cadastro inicial", usuario=request.user)
        messages.success(request, "Meta cadastrada.")
        return redirect(obj)
    return render(request, "metas/form.html", {"form": form, "titulo": "Nova meta"})


@login_required
def detalhe(request, pk):
    obj = get_object_or_404(_qs_usuario(request.user), pk=pk)
    return render(request, "metas/detalhe.html", {"meta": obj, "historico": obj.atualizacoes.all()})


@login_required
def editar(request, pk):
    obj = get_object_or_404(_qs_usuario(request.user), pk=pk)
    form = MetaExecucaoForm(request.POST or None, instance=obj)
    if form.is_valid():
        atualizado = form.save(commit=False)
        atualizado.atualizado_por = request.user
        atualizado.save()
        AtualizacaoMeta.objects.create(meta=atualizado, valor_realizado=atualizado.valor_realizado, situacao=atualizado.situacao, observacao=atualizado.justificativa, usuario=request.user)
        messages.success(request, "Meta atualizada e registrada no histórico.")
        return redirect(atualizado)
    return render(request, "metas/form.html", {"form": form, "titulo": "Atualizar meta", "meta": obj})
