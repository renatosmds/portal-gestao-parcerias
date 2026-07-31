from django.urls import path

from .views import (
    EmpresaCreate,
    EmpresaDelete,
    EmpresaDetail,
    EmpresaEdit,
    EmpresaList,
)


urlpatterns = [
    path("", EmpresaList.as_view(), name="list_empresas"),
    path("novo/", EmpresaCreate.as_view(), name="create_empresa"),
    path("<int:pk>/", EmpresaDetail.as_view(), name="detail_empresa"),
    path("<int:pk>/editar/", EmpresaEdit.as_view(), name="edit_empresa"),
    path("<int:pk>/excluir/", EmpresaDelete.as_view(), name="delete_empresa"),
]
