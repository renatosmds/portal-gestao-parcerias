from django.urls import path

from . import views

urlpatterns = [
    path("", views.painel, name="suporte_painel"),
    path("artigos/<slug:slug>/", views.artigo, name="suporte_artigo"),
    path("chamados/novo/", views.chamado_novo, name="suporte_chamado_novo"),
    path("chamados/<int:pk>/", views.chamado_detalhe, name="suporte_chamado_detalhe"),
    path("chamados/<int:pk>/responder/", views.chamado_responder, name="suporte_chamado_responder"),
]
