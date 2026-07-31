from django.urls import path

from .views import (
    AnaliseCreate,
    AnaliseDelete,
    AnaliseDetail,
    AnaliseList,
    AnaliseUpdate,
)


urlpatterns = [
    path("", AnaliseList.as_view(), name="list_analise"),
    path("novo/", AnaliseCreate.as_view(), name="create_analise"),
    path("<int:pk>/", AnaliseDetail.as_view(), name="detail_analise"),
    path("<int:pk>/editar/", AnaliseUpdate.as_view(), name="update_analise"),
    path("<int:pk>/excluir/", AnaliseDelete.as_view(), name="delete_analise"),
]
