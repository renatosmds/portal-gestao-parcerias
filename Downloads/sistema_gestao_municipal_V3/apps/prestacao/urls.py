from django.urls import path
from .views import (
    PrestacaoList,
    PrestacaoDelete,
    PrestacaoEdit,
    PrestacaoCreate,
    Pdf,
    PdfDebug,
)

from .views import relatorio_prestacao

urlpatterns = [
    path('', PrestacaoList.as_view(), name='list_prestacao'),
    path('novo/', PrestacaoCreate.as_view(), name='create_prestacao'),
    path('editar/<int:pk>/', PrestacaoEdit.as_view(), name='update_prestacao'),
    path('delete/<int:pk>/', PrestacaoDelete.as_view(), name='delete_prestacao'),
    path('relatorio_prestacao', relatorio_prestacao, name='relatorio_prestacao'),
    path('relatorio_prestacao_html', Pdf.as_view(), name='relatorio_prestacao_html'),
    path('relatorio_prestacao_html_debug', PdfDebug.as_view(), name='relatorio_prestacao_html_debug'),
]
