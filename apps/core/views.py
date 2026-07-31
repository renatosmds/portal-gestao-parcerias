# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.funcionarios.models import Funcionario
#from apps.parcerias.models import Parcerias  # ok
from apps.conferencia3.models import Conferencia3  # ok
from apps.receitas.models import Receitas
from apps.termos.models import Termos
from apps.parcerias.models import Parcerias

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from apps.core.serializers import UserSerializer, GroupSerializer
from apps.registro_hora_extra.models import RegistroHoraExtra
from apps.departamentos.models import Departamento
from django.core import serializers
from django.http import HttpResponse
from .tasks import send_relatorio
from django.db.models import Sum
from django.core.exceptions import PermissionDenied
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.template.loader import get_template
from django.urls import reverse

from .dashboard import montar_contexto_dashboard


@login_required
def home(request):
    """Dashboard integrado do Portal de Gestão de Parcerias."""
    contexto = montar_contexto_dashboard(request)
    return render(request, "core/index.html", contexto)


def menu(request):
    return render(request, 'core/principal1.html')


def execucao(request):
    return render(request, 'core/execucao.html')


def cadastros_gerais(request):
    return render(request, 'core/cadastros_gerais.html')


def funcionograma(request):
    return render(request, 'core/funcionograma.html')


def fornecedor(request):
    return render(request, 'core/cadastros_gerais/fornecedor.html')


def convocacao(request):
    return render(request, 'core/convocacao.html')


def form_convocacao(request):
    return render(request, 'core/form_convocacao.html')


def form_requerimento(request):
    return render(request, 'core/form_requerimento.html')


def form_habilitacao(request):
    return render(request, 'core/form_habilitacao.html')


def form_aprovacao(request):
    return render(request, 'core/form_aprovacao.html')


def monitoramento(request):
    return render(request, 'core/monitoramento.html')


def relatorio_gestor(request):
    return render(request, 'core/relatorio_gestor.html')


def relatorio_comissao(request):
    return render(request, 'core/relatorio_comissao.html')


def auditoria(request):
    return render(request, 'core/auditoria.html')


def analise_auditoria(request):
    return render(request, 'core/analise_auditoria.html')


def acompanhamento_auditorias(request):
    return render(request, 'core/acompanhamento_auditorias.html')


def tomada_contas(request):
    return render(request, 'core/tomada_contas.html')


def celery():
    send_relatorio.delay()
    return HttpResponse('Tarefa incluida na fila para execucao')


def departamentos_ajax(request):
    departamentos = Departamento.objects.all()
    return render(request, 'departamentos_ajax.html', {'departamentos': departamentos})


def filtra_funcionarios(request):
    func = request.GET['outro_param']
    funcionario = Departamento.objects.get(id=func)

    qs_json = serializers.serialize('json', funcionario.funcionario_set.all())
    return HttpResponse(qs_json, content_type='application/json')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


def filtra_termos(request):
    term = request.GET['outro_param']
    termos = Departamento.objects.get(id=term)

    qs_json = serializers.serialize('json', termos.funcionario_set.all())
    return HttpResponse(qs_json, content_type='application/json')


def filtra_prestacao(request):
    prest = request.GET['outro_param']
    prestacao = Departamento.objects.get(id=prest)

    qs_json = serializers.serialize('json', prestacao.funcionario_set.all())
    return HttpResponse(qs_json, content_type='application/json')


def filtra_conferencia3(request):
    confer = request.GET['outro_param']
    conferencia3 = Departamento.objects.get(id=confer)

    qs_json = serializers.serialize('json', conferencia3.funcionario_set.all())
    return HttpResponse(qs_json, content_type='application/json')


def conferencia3_list(request):
    data = {'usuario': request.user}
    funcionario = request.user.funcionario
    data['result'] = funcionario.empresa.total_funcionarios
    data['total_funcionarios'] = funcionario.empresa.total_funcionarios
    data['result1'] = funcionario.empresa.total_funcionarios_ferias
    data['total_funcionarios_ferias'] = funcionario.empresa.total_funcionarios_ferias
    data['result2'] = funcionario.empresa.total_funcionarios_doc_pendente
    data['total_funcionarios_doc_pendente'] = funcionario.empresa.total_funcionarios_doc_pendente
    data['result3'] = funcionario.empresa.total_funcionarios_doc_ok
    data['total_funcionarios_doc_ok'] = funcionario.empresa.total_funcionarios_doc_ok
    data['total_funcionarios_rg'] = 10
    data['result4'] = RegistroHoraExtra.objects.filter(
        funcionario__empresa=funcionario.empresa, utilizada=True).aggregate(Sum('horas'))['horas__sum'] or 0
    data['total_hora_extra_utilizadas'] = RegistroHoraExtra.objects.filter(
        funcionario__empresa=funcionario.empresa, utilizada=True).aggregate(Sum('horas'))['horas__sum'] or 0
    data['result5'] = RegistroHoraExtra.objects.filter(
        funcionario__empresa=funcionario.empresa, utilizada=False).aggregate(Sum('horas'))['horas__sum'] or 0
    data['total_hora_extra_pendente'] = RegistroHoraExtra.objects.filter(
        funcionario__empresa=funcionario.empresa, utilizada=False).aggregate(Sum('horas'))['horas__sum'] or 0

    return render(request, 'core/clientes_list.html', data)


def filtra_parcerias(request):
    parcer = request.GET['outro_param']
    parcerias = Departamento.objects.get(id=parcer)

    qs_json = serializers.serialize('json', parcerias.funcionario_set.all())
    return HttpResponse(qs_json, content_type='application/json')


def filtra_receitas(request):
    receit = request.GET['outro_param']
    receitas = Departamento.objects.get(id=receit)

    qs_json = serializers.serialize('json', receitas.funcionario_set.all())
    return HttpResponse(qs_json, content_type='application/json')


def analise(request):
    return self.Analise_set.all().count()


@staff_member_required
def diagnostico_portal(request):
    """Painel simples de homologação para administradores."""
    verificacoes = []

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        verificacoes.append({"nome": "Banco de dados", "ok": True, "detalhe": "Conexão realizada."})
    except Exception as exc:
        verificacoes.append({"nome": "Banco de dados", "ok": False, "detalhe": str(exc)})

    for nome_template in ("base.html", "core/index.html", "conciliacao/painel.html", "metas/painel.html"):
        try:
            get_template(nome_template)
            verificacoes.append({"nome": f"Template: {nome_template}", "ok": True, "detalhe": "Carregado corretamente."})
        except Exception as exc:
            verificacoes.append({"nome": f"Template: {nome_template}", "ok": False, "detalhe": str(exc)})

    for nome_rota in ("home", "conciliacao_painel", "metas_painel", "assistente_ia_central", "relatorios_painel"):
        try:
            endereco = reverse(nome_rota)
            verificacoes.append({"nome": f"Rota: {nome_rota}", "ok": True, "detalhe": endereco})
        except Exception as exc:
            verificacoes.append({"nome": f"Rota: {nome_rota}", "ok": False, "detalhe": str(exc)})

    return render(request, "core/diagnostico.html", {
        "verificacoes": verificacoes,
        "total_falhas": sum(not item["ok"] for item in verificacoes),
    })
