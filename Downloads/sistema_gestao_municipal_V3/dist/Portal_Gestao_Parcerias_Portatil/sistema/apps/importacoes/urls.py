from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista, name="list_importacoes"),
    path("nova/", views.nova, name="create_importacao"),
    path("<int:pk>/", views.detalhe, name="detail_importacao"),
    path("<int:pk>/confirmar/", views.confirmar, name="confirmar_importacao"),
    path("<int:pk>/cancelar/", views.cancelar, name="cancelar_importacao"),
]
