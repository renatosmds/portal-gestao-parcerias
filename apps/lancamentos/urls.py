from django.urls import path

from .views import (
    LancamentoCreate,
    LancamentoDelete,
    LancamentoDetail,
    LancamentoList,
    LancamentoUpdate,
    competencias_por_prestacao,
    prestacoes_por_termo,
    registrar_glosa,
)


urlpatterns = [
    path("", LancamentoList.as_view(), name="list_lancamentos"),
    path("novo/", LancamentoCreate.as_view(), name="create_lancamento"),
    path(
        "prestacoes-por-termo/",
        prestacoes_por_termo,
        name="prestacoes_por_termo",
    ),
    path(
        "competencias-por-prestacao/",
        competencias_por_prestacao,
        name="competencias_por_prestacao",
    ),
    path("<int:pk>/", LancamentoDetail.as_view(), name="detail_lancamento"),
    path("<int:pk>/glosa/", registrar_glosa, name="registrar_glosa"),
    path(
        "<int:pk>/editar/",
        LancamentoUpdate.as_view(),
        name="update_lancamento",
    ),
    path(
        "<int:pk>/excluir/",
        LancamentoDelete.as_view(),
        name="delete_lancamento",
    ),
]
