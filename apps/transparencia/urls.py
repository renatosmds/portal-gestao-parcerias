from django.urls import path
from . import views

urlpatterns = [
    path("", views.portal_publico, name="transparencia_publica"),
    path("parceria/<int:pk>/", views.parceria_publica, name="transparencia_parceria"),
    path("documento/<int:pk>/", views.documento_publico, name="transparencia_documento_publico"),
    path("dados-abertos.json", views.dados_abertos_json, name="transparencia_json"),
    path("dados-abertos.csv", views.dados_abertos_csv, name="transparencia_csv"),
    path("gestao/", views.painel_publicacao, name="transparencia_painel"),
    path("gestao/parceria/<int:termo_id>/", views.editar_publicacao_parceria, name="transparencia_editar_parceria"),
    path("gestao/documentos/", views.painel_documentos, name="transparencia_documentos"),
    path("gestao/documento/<int:documento_id>/", views.editar_publicacao_documento, name="transparencia_editar_documento"),
]
