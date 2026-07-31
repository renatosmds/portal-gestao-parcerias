from django.urls import path
from . import views

urlpatterns = [
    path("", views.painel_relatorios, name="relatorios_painel"),
    path("diligencias/", views.relatorio_diligencias, name="relatorio_diligencias"),
    path("diligencias.csv", views.relatorio_diligencias_csv, name="relatorio_diligencias_csv"),
    path("glosas/", views.relatorio_glosas, name="relatorio_glosas"),
    path("glosas.csv", views.relatorio_glosas_csv, name="relatorio_glosas_csv"),
    path("funcionarios/", views.relatorio_funcionarios, name="relatorio_funcionarios"),
    path("funcionarios.csv", views.relatorio_funcionarios_csv, name="relatorio_funcionarios_csv"),
    path("folha/", views.relatorio_folha, name="relatorio_folha"),
    path("folha.csv", views.relatorio_folha_csv, name="relatorio_folha_csv"),
]
