from django.urls import path
from .views import (
    FuncionariosList,
    FuncionarioEdit,
    FuncionarioDelete,
    FuncionarioCreate,
    Pdf,
    PdfDebug
)

from .views import relatorio_funcionario

urlpatterns = [
    path('', FuncionariosList.as_view(), name='list_funcionarios'),
    path('novo/', FuncionarioCreate.as_view(), name='create_funcionario'),
    path('editar/<int:pk>/', FuncionarioEdit.as_view(), name='update_funcionario'),
    path('delete/<int:pk>/', FuncionarioDelete.as_view(), name='delete_funcionario'),
    path('relatorio_funcionario', relatorio_funcionario, name='relatorio_funcionario'), # feito com reportlab
    path('relatorio_funcionario_html', Pdf.as_view(), name='relatorio_funcionario_html'),
    path('relatorio_funcionario_html_debug', PdfDebug.as_view(), name='relatorio_funcionario_html_debug'),
]
