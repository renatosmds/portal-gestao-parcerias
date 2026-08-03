from django.urls import path
from . import views

urlpatterns = [
    path("", views.painel, name="treinamento_painel"),
    path("modulo/<slug:slug>/", views.modulo, name="treinamento_modulo"),
    path("modulo/<slug:slug>/concluir/", views.concluir, name="treinamento_concluir"),
    path("reiniciar/", views.reiniciar, name="treinamento_reiniciar"),
    path("tour/concluir/", views.concluir_tour, name="treinamento_concluir_tour"),
]
