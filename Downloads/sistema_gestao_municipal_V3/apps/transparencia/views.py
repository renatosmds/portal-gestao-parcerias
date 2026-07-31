import csv
import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.documentos.models import Documento
from apps.termos.models import Termos
from .forms import PublicacaoDocumentoForm, PublicacaoParceriaForm
from .models import HistoricoPublicacao, PublicacaoDocumento, PublicacaoParceria


def _administrador(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _decimal(valor):
    return valor if isinstance(valor, Decimal) else Decimal(valor or 0)


def portal_publico(request):
    qs = (
        PublicacaoParceria.objects.filter(publicada=True)
        .select_related("termo", "termo__empresa")
        .order_by("termo__numtermo", "termo__termo")
    )
    busca = request.GET.get("q", "").strip()
    situacao = request.GET.get("situacao", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    if busca:
        qs = qs.filter(
            Q(termo__nomeosc__icontains=busca)
            | Q(termo__empresa__nome__icontains=busca)
            | Q(termo__numtermo__icontains=busca)
            | Q(termo__termo__icontains=busca)
            | Q(termo__objeto__icontains=busca)
        )
    if situacao:
        qs = qs.filter(termo__status__iexact=situacao)
    if tipo:
        qs = qs.filter(termo__tipo__iexact=tipo)

    base = PublicacaoParceria.objects.filter(publicada=True)
    totais = base.aggregate(
        valor_global=Sum("termo__valorglobal"),
        valor_repassado=Sum("termo__valorrepasse"),
    )
    context = {
        "publicacoes": qs,
        "busca": busca,
        "situacao": situacao,
        "tipo": tipo,
        "total_parcerias": base.count(),
        "total_oscs": base.values("termo__empresa_id", "termo__nomeosc").distinct().count(),
        "valor_global": totais["valor_global"] or 0,
        "valor_repassado": totais["valor_repassado"] or 0,
        "situacoes": [v for v in base.values_list("termo__status", flat=True).distinct() if v],
        "tipos": [v for v in base.values_list("termo__tipo", flat=True).distinct() if v],
    }
    return render(request, "transparencia/portal_publico.html", context)


def parceria_publica(request, pk):
    publicacao = get_object_or_404(
        PublicacaoParceria.objects.select_related("termo", "termo__empresa"),
        pk=pk,
        publicada=True,
    )
    termo = publicacao.termo
    documentos = (
        PublicacaoDocumento.objects.filter(
            publicado=True,
            classificacao=PublicacaoDocumento.Classificacao.PUBLICO,
            documento__termo=termo,
        )
        .select_related("documento")
        .order_by("documento__descricao")
    )
    return render(
        request,
        "transparencia/parceria_publica.html",
        {"publicacao": publicacao, "termo": termo, "documentos": documentos},
    )


def documento_publico(request, pk):
    publicacao = get_object_or_404(
        PublicacaoDocumento.objects.select_related("documento"),
        pk=pk,
        publicado=True,
        classificacao=PublicacaoDocumento.Classificacao.PUBLICO,
    )
    arquivo = publicacao.documento.arquivo
    if not arquivo:
        raise Http404("Arquivo não localizado.")
    return FileResponse(
        arquivo.open("rb"),
        as_attachment=False,
        filename=arquivo.name.rsplit("/", 1)[-1],
        content_type="application/octet-stream",
    )


def dados_abertos_json(request):
    dados = []
    for pub in PublicacaoParceria.objects.filter(publicada=True).select_related("termo", "termo__empresa"):
        t = pub.termo
        dados.append(
            {
                "numero_termo": t.numtermo or t.termo,
                "tipo": t.tipo,
                "osc": t.empresa.nome if t.empresa_id else t.nomeosc,
                "objeto": t.objeto,
                "vigencia_inicio": t.inicioVigencia,
                "vigencia_fim": t.terminoVigencia,
                "valor_global": str(t.valorglobal or "0.00"),
                "valor_repassado": str(t.valorrepasse or "0.00"),
                "situacao": t.status,
                "orgao_responsavel": pub.orgao_responsavel,
            }
        )
    return JsonResponse({"gerado_em": timezone.now().isoformat(), "resultados": dados}, json_dumps_params={"ensure_ascii": False})


def dados_abertos_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="parcerias_publicas.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Número do Termo", "Tipo", "OSC", "Objeto", "Início", "Término", "Valor Global", "Valor Repassado", "Situação", "Órgão"])
    for pub in PublicacaoParceria.objects.filter(publicada=True).select_related("termo", "termo__empresa"):
        t = pub.termo
        writer.writerow([
            t.numtermo or t.termo,
            t.tipo or "",
            t.empresa.nome if t.empresa_id else (t.nomeosc or ""),
            t.objeto or "",
            t.inicioVigencia or "",
            t.terminoVigencia or "",
            t.valorglobal or 0,
            t.valorrepasse or 0,
            t.status or "",
            pub.orgao_responsavel,
        ])
    return response


@login_required
@user_passes_test(_administrador)
def painel_publicacao(request):
    termos = Termos.objects.select_related("empresa").order_by("numtermo", "termo")
    busca = request.GET.get("q", "").strip()
    if busca:
        termos = termos.filter(Q(numtermo__icontains=busca) | Q(termo__icontains=busca) | Q(nomeosc__icontains=busca) | Q(empresa__nome__icontains=busca))
    publicacoes = {p.termo_id: p for p in PublicacaoParceria.objects.filter(termo__in=termos)}
    linhas = [{"termo": t, "publicacao": publicacoes.get(t.pk)} for t in termos]
    return render(request, "transparencia/painel_publicacao.html", {"linhas": linhas, "busca": busca})


@login_required
@user_passes_test(_administrador)
def editar_publicacao_parceria(request, termo_id):
    termo = get_object_or_404(Termos, pk=termo_id)
    obj, _ = PublicacaoParceria.objects.get_or_create(termo=termo)
    anterior = obj.publicada
    if request.method == "POST":
        form = PublicacaoParceriaForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.publicada_por = request.user
            obj.publicada_em = timezone.now() if obj.publicada else None
            obj.save()
            acao = HistoricoPublicacao.Acao.PUBLICAR if obj.publicada else HistoricoPublicacao.Acao.RETIRAR
            if anterior == obj.publicada:
                acao = HistoricoPublicacao.Acao.ALTERAR
            HistoricoPublicacao.objects.create(termo=termo, acao=acao, usuario=request.user, detalhes=obj.motivo_restricao or obj.resumo_publico)
            messages.success(request, "Configuração pública da parceria atualizada.")
            return redirect("transparencia_painel")
    else:
        form = PublicacaoParceriaForm(instance=obj)
    return render(request, "transparencia/editar_parceria.html", {"form": form, "termo": termo, "publicacao": obj})


@login_required
@user_passes_test(_administrador)
def painel_documentos(request):
    documentos = Documento.objects.select_related("empresa", "termo").order_by("descricao")
    busca = request.GET.get("q", "").strip()
    if busca:
        documentos = documentos.filter(Q(descricao__icontains=busca) | Q(numero_documento__icontains=busca) | Q(empresa__nome__icontains=busca))
    publicacoes = {p.documento_id: p for p in PublicacaoDocumento.objects.filter(documento__in=documentos)}
    linhas = [{"documento": d, "publicacao": publicacoes.get(d.pk)} for d in documentos]
    return render(request, "transparencia/painel_documentos.html", {"linhas": linhas, "busca": busca})


@login_required
@user_passes_test(_administrador)
def editar_publicacao_documento(request, documento_id):
    documento = get_object_or_404(Documento, pk=documento_id)
    obj, _ = PublicacaoDocumento.objects.get_or_create(documento=documento)
    anterior_publicado = obj.publicado
    anterior_classificacao = obj.classificacao
    if request.method == "POST":
        form = PublicacaoDocumentoForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.publicado_por = request.user
            obj.publicado_em = timezone.now() if obj.publicado else None
            obj.save()
            if anterior_classificacao != obj.classificacao:
                acao = HistoricoPublicacao.Acao.RECLASSIFICAR
            elif anterior_publicado != obj.publicado:
                acao = HistoricoPublicacao.Acao.PUBLICAR if obj.publicado else HistoricoPublicacao.Acao.RETIRAR
            else:
                acao = HistoricoPublicacao.Acao.ALTERAR
            HistoricoPublicacao.objects.create(documento=documento, acao=acao, usuario=request.user, detalhes=obj.motivo_restricao or obj.descricao_publica)
            messages.success(request, "Classificação e publicação do documento atualizadas.")
            return redirect("transparencia_documentos")
    else:
        form = PublicacaoDocumentoForm(instance=obj)
    return render(request, "transparencia/editar_documento.html", {"form": form, "documento": documento, "publicacao": obj})
