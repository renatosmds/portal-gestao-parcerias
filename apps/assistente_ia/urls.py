from django.urls import path

from .views import (
    CentralAssistenteIA,
    ExecutarAnaliseLocal,
    ProcessamentoDetalhe,
    RevisarProcessamento,
)

urlpatterns = [
    path("", CentralAssistenteIA.as_view(), name="assistente_ia_central"),
    path(
        "documento/<int:pk>/analisar/",
        ExecutarAnaliseLocal.as_view(),
        name="assistente_ia_executar",
    ),
    path(
        "processamento/<int:pk>/",
        ProcessamentoDetalhe.as_view(),
        name="assistente_ia_detalhe",
    ),
    path(
        "processamento/<int:pk>/revisar/",
        RevisarProcessamento.as_view(),
        name="assistente_ia_revisar",
    ),
]
