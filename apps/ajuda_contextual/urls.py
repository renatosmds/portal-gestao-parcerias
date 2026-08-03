from django.urls import path
from . import views

app_name = "ajuda_contextual"
urlpatterns = [
    path("resolver/", views.resolver, name="resolver"),
    path("gestao/", views.gestao, name="gestao"),
    path("<slug:chave>/avaliar/", views.avaliar, name="avaliar"),
    path("<slug:chave>/", views.detalhe, name="detalhe"),
]
