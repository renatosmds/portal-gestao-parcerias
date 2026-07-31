from django.urls import path
from .views import (
    FuncionariosList,
    FuncionarioEdit,
    FuncionarioDelete,
    FuncionarioCreate,
    Pdf,
    PdfDebug, folhas_ponto_list, folha_ponto_form, fechar_folha_ponto,
    folhas_pagamento_list, folha_pagamento_form, folha_pagamento_detail, fechar_folha_pagamento
)

from .views import relatorio_funcionario

urlpatterns = [
    path('ponto/', folhas_ponto_list, name='folhas_ponto_list'),
    path('ponto/novo/', folha_ponto_form, name='folha_ponto_create'),
    path('ponto/<int:pk>/editar/', folha_ponto_form, name='folha_ponto_update'),
    path('ponto/<int:pk>/fechar/', fechar_folha_ponto, name='folha_ponto_fechar'),
    path('folha/', folhas_pagamento_list, name='folhas_pagamento_list'),
    path('folha/nova/', folha_pagamento_form, name='folha_pagamento_create'),
    path('folha/<int:pk>/', folha_pagamento_detail, name='folha_pagamento_detail'),
    path('folha/<int:pk>/editar/', folha_pagamento_form, name='folha_pagamento_update'),
    path('folha/<int:pk>/fechar/', fechar_folha_pagamento, name='folha_pagamento_fechar'),
    path('', FuncionariosList.as_view(), name='list_funcionarios'),
    path('novo/', FuncionarioCreate.as_view(), name='create_funcionario'),
    path('editar/<int:pk>/', FuncionarioEdit.as_view(), name='update_funcionario'),
    path('delete/<int:pk>/', FuncionarioDelete.as_view(), name='delete_funcionario'),
    path('relatorio_funcionario', relatorio_funcionario, name='relatorio_funcionario'), # feito com reportlab
    path('relatorio_funcionario_html', Pdf.as_view(), name='relatorio_funcionario_html'),
    path('relatorio_funcionario_html_debug', PdfDebug.as_view(), name='relatorio_funcionario_html_debug'),
]
