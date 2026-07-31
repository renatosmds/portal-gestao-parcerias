from django.urls import path

from .views import (
    DepartamentoCreate,
    DepartamentoDelete,
    DepartamentoDetail,
    DepartamentoUpdate,
    DepartamentosList,
)


urlpatterns = [
    path("", DepartamentosList.as_view(), name="list_departamentos"),
    path("novo/", DepartamentoCreate.as_view(), name="create_departamento"),
    path("<int:pk>/", DepartamentoDetail.as_view(), name="detail_departamento"),
    path("<int:pk>/editar/", DepartamentoUpdate.as_view(), name="update_departamento"),
    path("<int:pk>/excluir/", DepartamentoDelete.as_view(), name="delete_departamento"),
]
