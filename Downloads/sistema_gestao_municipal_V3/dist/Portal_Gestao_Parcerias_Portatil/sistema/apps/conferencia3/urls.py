from django.urls import path
from .views import (
    Conferencia3List,
    Conferencia3Create,
    Conferencia3Update,
    Conferencia3Delete,
    Pdf,
    PdfDebug,
)

from .views import relatorio_conferencia3

urlpatterns = [
    path('list', Conferencia3List.as_view(), name='list_conferencia3'),
    path('novo', Conferencia3Create.as_view(), name='create_conferencia3'),
    path('update/<int:pk>/', Conferencia3Update.as_view(), name='update_conferencia3'),
    path('delete/<int:pk>/', Conferencia3Delete.as_view(), name='delete_conferencia3'),
    path('relatorio_conferencia3', relatorio_conferencia3, name='relatorio_conferencia3'),
    path('relatorio_conferencia3_html', Pdf.as_view(), name='relatorio_conferencia3_html'),
    path('relatorio_conferencia3_html_debug', PdfDebug.as_view(), name='relatorio_conferencia3_html_debug'),
]
