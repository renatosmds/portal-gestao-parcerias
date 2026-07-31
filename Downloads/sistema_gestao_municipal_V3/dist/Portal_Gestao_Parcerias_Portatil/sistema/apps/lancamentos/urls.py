from django.urls import path

from .views import (
    LancamentoCreate,
    LancamentoDelete,
    LancamentoDetail,
    LancamentoList,
    LancamentoUpdate,
    registrar_glosa,
)


urlpatterns = [
    path("", LancamentoList.as_view(), name="list_lancamentos"),
    path("novo/", LancamentoCreate.as_view(), name="create_lancamento"),
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
