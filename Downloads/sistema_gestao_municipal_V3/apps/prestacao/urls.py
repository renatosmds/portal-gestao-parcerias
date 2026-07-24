from django.urls import path

from .views import (
    PrestacaoCreate,
    PrestacaoDelete,
    PrestacaoDetail,
    PrestacaoEdit,
    PrestacaoList,
)


urlpatterns = [
    path("", PrestacaoList.as_view(), name="list_prestacao"),
    path("novo/", PrestacaoCreate.as_view(), name="create_prestacao"),
    path("<int:pk>/", PrestacaoDetail.as_view(), name="detail_prestacao"),
    path("<int:pk>/editar/", PrestacaoEdit.as_view(), name="update_prestacao"),
    path("<int:pk>/excluir/", PrestacaoDelete.as_view(), name="delete_prestacao"),
]
