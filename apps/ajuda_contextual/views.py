import re
import unicodedata

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .models import AjudaContextual, AcessoAjuda


# Correção Sprint 29: alguns formulários usam nomes técnicos curtos ou legados.
# O resolvedor converte esses nomes para os campos do manual sem alterar os formulários.
ALIASES_CAMPO = {
    "empresa": ["empresa", "osc", "razao_social"],
    "termo": ["termo", "numero", "numero_termo"],
    "inicio": ["inicio", "inicio_vigencia", "data_inicio"],
    "fim": ["fim", "fim_vigencia", "data_fim"],
    "valor": ["valor", "valor_global", "valor_lancamento", "valor_documento"],
    "data": ["data", "data_pagamento", "data_emissao"],
    "descricao": ["descricao", "objeto"],
    "numero": ["numero", "numero_documento", "numero_termo"],
    "competencia": ["competencia", "periodo"],
    "saldo_inicial": ["saldo_inicial"],
    "saldo_final": ["saldo_final", "saldo_final_informado"],
    "valor_previsto": ["valor_previsto"],
    "valor_realizado": ["valor_realizado"],
    "prazo": ["prazo", "prazo_resposta"],
}

ALIASES_MODULO = {
    "termo": "termos",
    "termos": "termos",
    "prestacao": "prestacoes",
    "prestacoes": "prestacoes",
    "lancamento": "lancamentos",
    "lancamentos": "lancamentos",
    "documento": "documentos",
    "documentos": "documentos",
    "conciliacao": "conciliacao",
    "metas": "metas",
    "diligencias": "diligencias",
    "parcerias": "parcerias",
    "empresas": "oscs",
}


def _normalizar(valor):
    valor = unicodedata.normalize("NFKD", valor or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", valor.lower()).strip("_")


def _permitida(request, ajuda):
    return request.user.is_authenticated or ajuda.publica


def _candidatos_campo(campo, label=""):
    normalizado = _normalizar(campo)
    candidatos = [normalizado]
    candidatos.extend(ALIASES_CAMPO.get(normalizado, []))
    label_normalizado = _normalizar(label)
    if label_normalizado:
        candidatos.append(label_normalizado)
        for token in label_normalizado.split("_"):
            candidatos.extend(ALIASES_CAMPO.get(token, [token]))
    # Remove repetidos preservando a ordem.
    return list(dict.fromkeys(filter(None, candidatos)))


def _detectar_modulos(caminho):
    partes = [_normalizar(p) for p in (caminho or "").strip("/").split("/") if p]
    modulos = []
    for parte in partes:
        modulos.append(ALIASES_MODULO.get(parte, parte))
    return list(dict.fromkeys(filter(None, modulos)))


@require_GET
def detalhe(request, chave):
    ajuda = AjudaContextual.objects.filter(chave=chave, ativo=True).first()
    if not ajuda or not _permitida(request, ajuda):
        return JsonResponse({"detail": "Orientação não encontrada ou indisponível."}, status=404)
    AcessoAjuda.objects.create(
        ajuda=ajuda,
        usuario=request.user if request.user.is_authenticated else None,
        caminho=request.GET.get("path", "")[:300],
    )
    return JsonResponse(ajuda.as_dict())


@require_GET
def resolver(request):
    campo = request.GET.get("campo", "").strip()
    label = request.GET.get("label", "").strip()
    caminho = request.GET.get("path", "").strip()
    if not campo:
        return JsonResponse({"detail": "Campo não informado."}, status=400)

    candidatos = _candidatos_campo(campo, label)
    modulos = _detectar_modulos(caminho)

    qs = AjudaContextual.objects.filter(ativo=True)
    condicao = Q()
    for candidato in candidatos:
        condicao |= Q(campo__iexact=candidato)
        condicao |= Q(chave__iendswith=f".{candidato}")
    encontrados = qs.filter(condicao) if condicao else qs.none()

    ajuda = None
    for modulo in modulos:
        ajuda = encontrados.filter(modulo__iexact=modulo).first()
        if ajuda:
            break
    ajuda = ajuda or encontrados.filter(modulo="geral").first() or encontrados.first()

    # Última tentativa: comparação segura com título e ajuda curta, usando o rótulo.
    if not ajuda and label:
        termos = [t for t in _normalizar(label).split("_") if len(t) > 2]
        busca = Q()
        for termo in termos:
            busca |= Q(titulo__icontains=termo) | Q(ajuda_curta__icontains=termo)
        candidatos_texto = qs.filter(busca) if busca else qs.none()
        for modulo in modulos:
            ajuda = candidatos_texto.filter(modulo__iexact=modulo).first()
            if ajuda:
                break
        ajuda = ajuda or candidatos_texto.first()

    if not ajuda or not _permitida(request, ajuda):
        return JsonResponse({"disponivel": False})
    return JsonResponse({
        "disponivel": True,
        "chave": ajuda.chave,
        "titulo": ajuda.titulo,
        "ajuda_curta": ajuda.ajuda_curta,
    })


@require_POST
def avaliar(request, chave):
    ajuda = AjudaContextual.objects.filter(chave=chave, ativo=True).first()
    if not ajuda or not _permitida(request, ajuda):
        return JsonResponse({"detail": "Ajuda não encontrada."}, status=404)
    valor = request.POST.get("util")
    AcessoAjuda.objects.create(
        ajuda=ajuda,
        usuario=request.user if request.user.is_authenticated else None,
        caminho=request.POST.get("path", "")[:300],
        util=valor == "1",
    )
    return JsonResponse({"ok": True})


@login_required
@user_passes_test(lambda u: u.is_staff)
def gestao(request):
    ajudas = AjudaContextual.objects.all()
    modulo = request.GET.get("modulo", "")
    q = request.GET.get("q", "")
    if modulo:
        ajudas = ajudas.filter(modulo=modulo)
    if q:
        ajudas = ajudas.filter(Q(titulo__icontains=q) | Q(chave__icontains=q) | Q(campo__icontains=q))
    return render(request, "ajuda_contextual/gestao.html", {
        "ajudas": ajudas[:300],
        "modulos": AjudaContextual.objects.values_list("modulo", flat=True).distinct(),
        "q": q,
        "modulo_atual": modulo,
    })
