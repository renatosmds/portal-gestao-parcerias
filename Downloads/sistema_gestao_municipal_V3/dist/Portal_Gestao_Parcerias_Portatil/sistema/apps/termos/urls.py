from django.urls import path

from .views import TermosCreate, TermosDelete, TermosDetail, TermosList, TermosUpdate


urlpatterns = [
    path("", TermosList.as_view(), name="list_termos"),
    path("novo/", TermosCreate.as_view(), name="create_termos"),
    path("<int:pk>/", TermosDetail.as_view(), name="detail_termo"),
    path("<int:pk>/editar/", TermosUpdate.as_view(), name="update_termos"),
    path("<int:pk>/excluir/", TermosDelete.as_view(), name="delete_termos"),
]
