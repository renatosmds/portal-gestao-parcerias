from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .conteudo import FAQ, MODULOS, obter_modulo
from .models import PreferenciaTour, ProgressoTreinamento


def _perfil(user):
    if user.is_superuser or user.is_staff:
        return "administrador"
    # Compatível com perfis existentes sem criar dependência rígida.
    texto = " ".join(str(getattr(user, a, "")) for a in ("perfil", "tipo_usuario", "groups"))
    texto = texto.lower()
    return "osc" if "osc" in texto else "orgao"


def _visiveis(user):
    perfil = _perfil(user)
    return [m for m in MODULOS if "todos" in m["perfis"] or perfil in m["perfis"] or (perfil == "administrador" and "orgao" in m["perfis"])]


@login_required
def painel(request):
    modulos = _visiveis(request.user)
    concluidos = set(ProgressoTreinamento.objects.filter(usuario=request.user, concluido=True).values_list("modulo", flat=True))
    itens = [{**m, "concluido": m["slug"] in concluidos} for m in modulos]
    total = len(itens)
    quantidade = sum(1 for item in itens if item["concluido"])
    percentual = round((quantidade / total) * 100) if total else 0
    preferencia, _ = PreferenciaTour.objects.get_or_create(usuario=request.user)
    return render(request, "treinamento/painel.html", {
        "modulos": itens, "faq": FAQ, "total": total, "quantidade": quantidade,
        "percentual": percentual, "tour_concluido": preferencia.tour_concluido,
    })


@login_required
def modulo(request, slug):
    item = obter_modulo(slug)
    if not item or item not in _visiveis(request.user):
        raise Http404("Treinamento não encontrado")
    progresso, _ = ProgressoTreinamento.objects.get_or_create(usuario=request.user, modulo=slug)
    return render(request, "treinamento/modulo.html", {"modulo": item, "progresso": progresso})


@login_required
@require_POST
def concluir(request, slug):
    item = obter_modulo(slug)
    if not item or item not in _visiveis(request.user):
        raise Http404("Treinamento não encontrado")
    progresso, _ = ProgressoTreinamento.objects.get_or_create(usuario=request.user, modulo=slug)
    progresso.concluido = request.POST.get("concluido", "1") == "1"
    progresso.save(update_fields=["concluido", "atualizado_em"])
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "concluido": progresso.concluido})
    return redirect("treinamento_modulo", slug=slug)


@login_required
@require_POST
def reiniciar(request):
    ProgressoTreinamento.objects.filter(usuario=request.user).update(concluido=False)
    PreferenciaTour.objects.update_or_create(usuario=request.user, defaults={"tour_concluido": False})
    return redirect("treinamento_painel")


@login_required
@require_POST
def concluir_tour(request):
    PreferenciaTour.objects.update_or_create(usuario=request.user, defaults={"tour_concluido": True})
    return JsonResponse({"ok": True})
