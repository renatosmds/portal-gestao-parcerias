from django.urls import path
from .views import home, celery, filtra_funcionarios, departamentos_ajax, filtra_termos, filtra_prestacao,\
    filtra_conferencia3, filtra_parcerias, filtra_receitas, execucao, cadastros_gerais, funcionograma, convocacao, form_convocacao,\
    form_requerimento, form_habilitacao, form_aprovacao, relatorio_gestor, relatorio_comissao,  monitoramento,\
    auditoria, analise_auditoria, acompanhamento_auditorias, tomada_contas, analise, conferencia3_list, menu, diagnostico_portal


from .views_sprint32 import (
    execucao_em_desenvolvimento,
    financeiro_em_desenvolvimento,
)

from .acessos_views import (
    acessos_grupo,
    acessos_grupo_novo,
    acessos_painel,
    acessos_usuario,
    acessos_usuario_grupos,
)

from .dashboard_acessos_views import (
    dashboard_acessos_grupo,
    dashboard_acessos_painel,
    dashboard_acessos_usuario,
)

urlpatterns = [
    path(
        "acessos/",
        acessos_painel,
        name="acessos_painel",
    ),
    path(
        "acessos/usuarios/<int:pk>/",
        acessos_usuario,
        name="acessos_usuario",
    ),
    path(
        "acessos/usuarios/<int:pk>/grupos/",
        acessos_usuario_grupos,
        name="acessos_usuario_grupos",
    ),
    path(
        "acessos/grupos/novo/",
        acessos_grupo_novo,
        name="acessos_grupo_novo",
    ),
    path(
        "acessos/grupos/<int:pk>/",
        acessos_grupo,
        name="acessos_grupo",
    ),


    path(
        "acessos/dashboard/",
        dashboard_acessos_painel,
        name="dashboard_acessos_painel",
    ),
    path(
        "acessos/dashboard/usuarios/<int:pk>/",
        dashboard_acessos_usuario,
        name="dashboard_acessos_usuario",
    ),
    path(
        "acessos/dashboard/grupos/<int:pk>/",
        dashboard_acessos_grupo,
        name="dashboard_acessos_grupo",
    ),


    path(
        "execucao/em-desenvolvimento/",
        execucao_em_desenvolvimento,
        name="execucao_em_desenvolvimento",
    ),
    path(
        "financeiro/em-desenvolvimento/",
        financeiro_em_desenvolvimento,
        name="financeiro_em_desenvolvimento",
    ),

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
    path('diagnostico/', diagnostico_portal, name='diagnostico_portal'),
]
