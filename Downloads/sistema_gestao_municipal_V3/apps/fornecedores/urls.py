from django.urls import path
from .views import (
    FornecedoresList,
    FornecedorCreate,
    FornecedorUpdate,
    FornecedorDelete,
    Pdf,
    PdfDebug,
)

from .views import relatorio_fornecedor

urlpatterns = [
    path('list', FornecedoresList.as_view(), name='list_fornecedores'),
    path('novo', FornecedorCreate.as_view(), name='create_fornecedor'),
    path('update/<int:pk>/', FornecedorUpdate.as_view(), name='update_fornecedor'),
    path('delete/<int:pk>/', FornecedorDelete.as_view(), name='delete_fornecedor'),
    path('relatorio_fornecedor', relatorio_fornecedor, name='relatorio_fornecedor'),
    path('relatorio_fornecedor_html', Pdf.as_view(), name='relatorio_fornecedor_html'),
    path('relatorio_fornecedor_html_debug', PdfDebug.as_view(), name='relatorio_fornecedor_html_debug'),
]
