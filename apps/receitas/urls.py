from django.urls import path
from .views import (
    ReceitasList,
    ReceitasCreate,
    ReceitasUpdate,
    ReceitasDelete,
    Pdf,
    PdfDebug,
)

from .views import relatorio_receitas

urlpatterns = [
    path('list', ReceitasList.as_view(), name='list_receitas'),
    path('novo', ReceitasCreate.as_view(), name='create_receitas'),
    path('update/<int:pk>/', ReceitasUpdate.as_view(), name='update_receitas'),
    path('delete/<int:pk>/', ReceitasDelete.as_view(), name='delete_receitas'),
    path('relatorio_receitas', relatorio_receitas, name='relatorio_receitas'),
    path('relatorio_receitas_html', Pdf.as_view(), name='relatorio_receitas_html'),
    path('relatorio_receitas_html_debug', PdfDebug.as_view(), name='relatorio_receitas_html_debug'),
]
