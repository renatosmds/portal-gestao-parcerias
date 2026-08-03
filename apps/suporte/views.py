from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ChamadoSuporteForm, InteracaoChamadoForm
from .models import ArtigoConhecimento, ChamadoSuporte


def _chamados_visiveis(user):
    qs = ChamadoSuporte.objects.select_related("solicitante", "responsavel")
    return qs if (user.is_staff or user.is_superuser) else qs.filter(solicitante=user)


@login_required
def painel(request):
    q = request.GET.get("q", "").strip()
    artigos = ArtigoConhecimento.objects.filter(ativo=True)
    if q:
        artigos = artigos.filter(Q(titulo__icontains=q) | Q(resumo__icontains=q) | Q(conteudo__icontains=q))
    chamados = _chamados_visiveis(request.user)[:8]
    return render(request, "suporte/painel.html", {"artigos": artigos[:12], "chamados": chamados, "q": q})


@login_required
def artigo(request, slug):
    item = get_object_or_404(ArtigoConhecimento, slug=slug, ativo=True)
    if not item.publico and not request.user.is_authenticated:
        raise Http404
    return render(request, "suporte/artigo.html", {"artigo": item})


@login_required
def chamado_novo(request):
    inicial = {"pagina_origem": request.GET.get("origem", "")}
    form = ChamadoSuporteForm(request.POST or None, request.FILES or None, initial=inicial)
    if request.method == "POST" and form.is_valid():
        chamado = form.save(commit=False)
        chamado.solicitante = request.user
        chamado.save()
        messages.success(request, f"Chamado #{chamado.pk} aberto com sucesso.")
        return redirect("suporte_chamado_detalhe", pk=chamado.pk)
    return render(request, "suporte/chamado_form.html", {"form": form})


@login_required
def chamado_detalhe(request, pk):
    chamado = get_object_or_404(_chamados_visiveis(request.user), pk=pk)
    interacoes = chamado.interacoes.select_related("autor")
    if not (request.user.is_staff or request.user.is_superuser):
        interacoes = interacoes.filter(interno=False)
    form = InteracaoChamadoForm()
    return render(request, "suporte/chamado_detalhe.html", {"chamado": chamado, "interacoes": interacoes, "form": form})


@login_required
@require_POST
def chamado_responder(request, pk):
    chamado = get_object_or_404(_chamados_visiveis(request.user), pk=pk)
    form = InteracaoChamadoForm(request.POST)
    if form.is_valid():
        interacao = form.save(commit=False)
        interacao.chamado = chamado
        interacao.autor = request.user
        interacao.save()
        if chamado.situacao in {"resolvido", "encerrado"}:
            chamado.situacao = "aberto"
            chamado.save(update_fields=["situacao", "atualizado_em"])
        messages.success(request, "Resposta registrada.")
    return redirect("suporte_chamado_detalhe", pk=chamado.pk)
