from django.urls import path

from .views import (
    DocumentoConferencia,
    DocumentoCreate,
    DocumentoDelete,
    DocumentoDetail,
    DocumentoList,
    DocumentoUpdate,
)


urlpatterns = [
    path("", DocumentoList.as_view(), name="list_documentos"),
    path("novo/", DocumentoCreate.as_view(), name="create_documento"),
    path("<int:pk>/", DocumentoDetail.as_view(), name="detail_documento"),
    path(
        "<int:pk>/editar/",
        DocumentoUpdate.as_view(),
        name="update_documento",
    ),
    path(
        "<int:pk>/conferir/",
        DocumentoConferencia.as_view(),
        name="conferir_documento",
    ),
    path(
        "<int:pk>/excluir/",
        DocumentoDelete.as_view(),
        name="delete_documento",
    ),
]
