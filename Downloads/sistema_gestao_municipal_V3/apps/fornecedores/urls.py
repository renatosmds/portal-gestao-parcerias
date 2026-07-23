from django.urls import path

from .views import (
    FornecedorCreate,
    FornecedorDelete,
    FornecedorDetail,
    FornecedorUpdate,
    FornecedoresList,
)


urlpatterns = [
    path("", FornecedoresList.as_view(), name="list_fornecedores"),
    path("novo/", FornecedorCreate.as_view(), name="create_fornecedor"),
    path("<int:pk>/", FornecedorDetail.as_view(), name="detail_fornecedor"),
    path("<int:pk>/editar/", FornecedorUpdate.as_view(), name="update_fornecedor"),
    path("<int:pk>/excluir/", FornecedorDelete.as_view(), name="delete_fornecedor"),
]
