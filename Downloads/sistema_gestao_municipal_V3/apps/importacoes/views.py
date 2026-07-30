from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ImportacaoUploadForm
from .models import Importacao
from .services import confirmar_importacao, ler_arquivo, validar_linhas


def pode_importar(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.has_perm("importacoes.add_importacao"))


@login_required
def lista(request):
    return render(request, "importacoes/list.html", {"importacoes": Importacao.objects.all()[:100]})


@login_required
@user_passes_test(pode_importar)
def nova(request):
    if request.method == "POST":
        form = ImportacaoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = form.cleaned_data["arquivo"]
            try:
                cabecalhos, linhas = ler_arquivo(arquivo)
                erros = validar_linhas(form.cleaned_data["tipo"], linhas)
                obj = Importacao.objects.create(
                    tipo=form.cleaned_data["tipo"], arquivo_nome=arquivo.name,
                    sistema_origem=form.cleaned_data["sistema_origem"] or "Arquivo externo",
                    cabecalhos=cabecalhos, linhas=linhas, erros=erros,
                    total_lido=len(linhas), total_erros=len(erros), criado_por=request.user,
                )
                return redirect("detail_importacao", pk=obj.pk)
            except Exception as exc:
                form.add_error("arquivo", str(exc))
    else:
        form = ImportacaoUploadForm()
    return render(request, "importacoes/form.html", {"form": form})


@login_required
def detalhe(request, pk):
    obj = get_object_or_404(Importacao, pk=pk)
    return render(request, "importacoes/detail.html", {"importacao": obj, "amostra": obj.linhas[:20]})


@login_required
@user_passes_test(pode_importar)
@require_POST
def confirmar(request, pk):
    obj = get_object_or_404(Importacao, pk=pk, situacao=Importacao.Situacao.VALIDACAO)
    confirmar_importacao(obj)
    messages.success(request, "Importação processada. Confira o resumo e eventuais erros.")
    return redirect("detail_importacao", pk=obj.pk)


@login_required
@user_passes_test(pode_importar)
@require_POST
def cancelar(request, pk):
    obj = get_object_or_404(Importacao, pk=pk, situacao=Importacao.Situacao.VALIDACAO)
    obj.situacao = Importacao.Situacao.CANCELADA
    obj.save(update_fields=["situacao"])
    messages.info(request, "Importação cancelada sem alterar os cadastros.")
    return redirect("detail_importacao", pk=obj.pk)
