from django.urls import path
from . import views

urlpatterns = [
    path("", views.painel, name="metas_painel"),
    path("nova/", views.nova, name="metas_nova"),
    path("<int:pk>/", views.detalhe, name="metas_detalhe"),
    path("<int:pk>/editar/", views.editar, name="metas_editar"),
]
