from django.urls import path
from .views import (
    ClientesList,
    ClientesCreate,
    ClientesUpdate,
    ClientesDelete,
    Pdf,
    PdfDebug,
)

from .views import relatorio_clientes

urlpatterns = [
    path('list', ClientesList.as_view(), name='list_clientes'),
    path('novo', ClientesCreate.as_view(), name='create_clientes'),
    path('update/<int:pk>/', ClientesUpdate.as_view(), name='update_clientes'),
    path('delete/<int:pk>/', ClientesDelete.as_view(), name='delete_clientes'),
    path('relatorio_clientes', relatorio_clientes, name='relatorio_clientes'),
    path('relatorio_clientes_html', Pdf.as_view(), name='relatorio_clientes_html'),
    path('relatorio_clientes_html_debug', PdfDebug.as_view(), name='relatorio_clientes_html_debug'),
]
