from django.urls import path

from . import views


app_name = "planos_trabalho"


urlpatterns = [
    path(
        "",
        views.plano_lista,
        name="plano_lista",
    ),

    path(
        "novo/",
        views.plano_criar,
        name="plano_criar",
    ),

    path(
        "<int:pk>/",
        views.plano_detalhe,
        name="plano_detalhe",
    ),

    path(
        "<int:pk>/editar/",
        views.plano_editar,
        name="plano_editar",
    ),

    path(
        "<int:pk>/analise/",
        views.plano_analise,
        name="plano_analise",
    ),

    path(
        "<int:plano_pk>/itens/novo/",
        views.item_criar,
        name="item_criar",
    ),

    path(
        "itens/<int:pk>/editar/",
        views.item_editar,
        name="item_editar",
    ),

    path(
        "itens/<int:pk>/analise/",
        views.item_analise,
        name="item_analise",
    ),
]
