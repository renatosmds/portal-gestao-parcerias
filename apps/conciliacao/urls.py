from django.urls import path
from . import views

urlpatterns = [
    path("", views.painel, name="conciliacao_painel"),
    path("nova/", views.nova, name="conciliacao_nova"),
    path("<int:pk>/", views.detalhe, name="conciliacao_detalhe"),
    path("<int:pk>/importar/", views.importar, name="conciliacao_importar"),
    path("<int:pk>/movimentacao/", views.adicionar_movimentacao, name="conciliacao_movimentacao_adicionar"),
    path("movimentacao/<int:mov_pk>/vincular/", views.vincular, name="conciliacao_vincular"),
    path("movimentacao/<int:mov_pk>/ignorar/", views.ignorar, name="conciliacao_ignorar"),
    path("vinculo/<int:pk>/excluir/", views.excluir_vinculo, name="conciliacao_vinculo_excluir"),
    path("ocorrencia/<int:pk>/", views.atualizar_ocorrencia, name="conciliacao_ocorrencia_atualizar"),
]
