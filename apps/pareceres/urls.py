from django.urls import path

from apps.pareceres import views


app_name = "pareceres"


urlpatterns = [
    path(
        "",
        views.parecer_lista,
        name="parecer_lista",
    ),
    path(
        "<int:pk>/",
        views.parecer_detalhe,
        name="parecer_detalhe",
    ),
    path(
        "<int:pk>/revisar/",
        views.parecer_revisar,
        name="parecer_revisar",
    ),
    path(
        "<int:pk>/nova-versao/",
        views.parecer_nova_versao,
        name="parecer_nova_versao",
    ),
    path(
        "<int:pk>/aprovar/",
        views.parecer_aprovar,
        name="parecer_aprovar",
    ),
    path(
        "itens/<int:pk>/revisar/",
        views.item_revisar,
        name="item_revisar",
    ),
]
