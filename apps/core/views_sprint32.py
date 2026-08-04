from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def execucao_em_desenvolvimento(request):
    return render(request, "core/modulo_em_desenvolvimento.html", {"modulo": "Execução"})


@login_required
def financeiro_em_desenvolvimento(request):
    return render(request, "core/modulo_em_desenvolvimento.html", {"modulo": "Financeiro"})
