from django.urls import path
from .views import (
    TermosList,
    TermosUpdate,
    TermosDelete,
    TermosCreate,
    Pdf,
    PdfDebug,
)

from .views import relatorio_termos

urlpatterns = [
    path('', TermosList.as_view(), name='list_termos'),
    path('novo/', TermosCreate.as_view(), name='create_termos'),
    path('editar/<int:pk>/', TermosUpdate.as_view(), name='update_termos'),
    path('delete/<int:pk>/', TermosDelete.as_view(), name='delete_termos'),
    path('relatorio_termos', relatorio_termos, name='relatorio_termos'),
    path('relatorio_termos_html', Pdf.as_view(), name='relatorio_termos_html'),
    path('relatorio_termos_html_debug', PdfDebug.as_view(), name='relatorio_termos_html_debug'),
]
