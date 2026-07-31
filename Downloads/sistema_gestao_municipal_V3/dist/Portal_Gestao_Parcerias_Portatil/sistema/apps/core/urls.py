from django.urls import path
from .views import home, celery, filtra_funcionarios, departamentos_ajax, filtra_termos, filtra_prestacao,\
    filtra_conferencia3, filtra_parcerias, filtra_receitas, execucao, cadastros_gerais, funcionograma, convocacao, form_convocacao,\
    form_requerimento, form_habilitacao, form_aprovacao, relatorio_gestor, relatorio_comissao,  monitoramento,\
    auditoria, analise_auditoria, acompanhamento_auditorias, tomada_contas, analise, conferencia3_list, menu

urlpatterns = [
    path('', home, name='home'),
    path('execucao/', execucao, name='execucao'),
    path('conferencia3_list/', conferencia3_list, name='conferencia3_list'),
    path('funcionograma/', funcionograma, name='funcionograma'),
    path('cadastros_gerais/', cadastros_gerais, name='cadastros_gerais'),
    path('convocacao/', convocacao, name='convocacao'),
    path('form_convocacao/', form_convocacao, name='form_convocacao'),
    path('form_requerimento/', form_requerimento, name='form_requerimento'),
    path('form_habilitacao/', form_habilitacao, name='form_habilitacao'),
    path('form_aprovacao/', form_aprovacao, name='form_aprovacao'),
    path('monitoramento/', monitoramento, name='monitoramento'),
    path('relatorio_gestor/', relatorio_gestor, name='relatorio_gestor'),
    path('relatorio_comissao/', relatorio_comissao, name='relatorio_comissao'),
    path('auditoria/', auditoria, name='auditoria'),
    path('analise_auditoria/', analise_auditoria, name='analise_auditoria'),
    path('acompanhamento_auditorias/', acompanhamento_auditorias, name='acompanhamento_auditorias'),
    path('tomada_contas/', tomada_contas, name='tomada_contas'),
    path('celery/', celery, name='celery'),
    path('departamentos-ajax/', departamentos_ajax, name='departamentos_ajax'),
    path('filtra-funcionarios/', filtra_funcionarios, name='filtra_funcionarios'),
    path('filtra-prestacao/', filtra_prestacao, name='filtra_prestacao'),
    path('filtra-termos/', filtra_termos, name='filtra_termos'),
    path('filtra_conferencia3/', filtra_conferencia3, name='filtra_conferencia3'),
    path('filtra-parcerias/', filtra_parcerias, name='filtra_parcerias'),
    path('filtra-receitas/', filtra_receitas, name='filtra_receitas'),
    path(
        'analise-legado/',
        analise,
        name='analise_legado',
    ),
    path('menu/', menu, name='menu'),
]
