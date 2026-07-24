from django.urls import path

from .views import (
    ParceriaCreate,
    ParceriaDelete,
    ParceriaDetail,
    ParceriaUpdate,
    ParceriasList,
)


urlpatterns = [
    path("", ParceriasList.as_view(), name="list_parcerias"),
    path("novo/", ParceriaCreate.as_view(), name="create_parceria"),
    path("<int:pk>/", ParceriaDetail.as_view(), name="detail_parceria"),
    path("<int:pk>/editar/", ParceriaUpdate.as_view(), name="update_parceria"),
    path("<int:pk>/excluir/", ParceriaDelete.as_view(), name="delete_parceria"),
]
