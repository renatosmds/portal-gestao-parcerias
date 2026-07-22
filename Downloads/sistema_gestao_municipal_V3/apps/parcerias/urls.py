from django.urls import path
from .views import (
    ParceriasList,
    ParceriaCreate,
    ParceriaUpdate,
    ParceriaDelete,
    Pdf,
    PdfDebug,
)

from .views import relatorio_parcerias

urlpatterns = [
    path('list', ParceriasList.as_view(), name='list_parcerias'),
    path('novo', ParceriaCreate.as_view(), name='create_parceria'),
    path('update/<int:pk>/', ParceriaUpdate.as_view(), name='update_parceria'),
    path('delete/<int:pk>/', ParceriaDelete.as_view(), name='delete_parceria'),
    path('relatorio_parcerias', relatorio_parcerias, name='relatorio_parceria'),
    path('relatorio_parceria_html', Pdf.as_view(), name='relatorio_parceria_html'),
    path('relatorio_parceria_html_debug', PdfDebug.as_view(), name='relatorio_parceria_html_debug'),
]
