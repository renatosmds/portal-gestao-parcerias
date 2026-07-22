from django.urls import path
from .views import (
    AnaliseList,
    AnaliseCreate,
    AnaliseUpdate,
    AnaliseDelete,
    Pdf,
    PdfDebug,
)

from .views import relatorio_analise

urlpatterns = [
    path('list', AnaliseList.as_view(), name='list_analise'),
    path('novo', AnaliseCreate.as_view(), name='create_analise'),
    path('update/<int:pk>/', AnaliseUpdate.as_view(), name='update_analise'),
    path('delete/<int:pk>/', AnaliseDelete.as_view(), name='delete_analise'),
    path('relatorio_analise', relatorio_analise, name='relatorio_analise'),
    path('relatorio_analise_html', Pdf.as_view(), name='relatorio_analise_html'),
    path('relatorio_analise_html_debug', PdfDebug.as_view(), name='relatorio_analise_html_debug'),
]
