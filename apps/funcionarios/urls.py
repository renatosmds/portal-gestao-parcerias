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

from .views import relatorio_funcionario, gerenciar_acesso_funcionario

from .views_cadastros import (
    CargoCreate,
    CargoDelete,
    CargoList,
    CargoUpdate,
    EquipamentoCreate,
    EquipamentoDelete,
    EquipamentoList,
    EquipamentoUpdate,
    NivelCreate,
    NivelDelete,
    NivelList,
    NivelUpdate,
)


urlpatterns = [
    path(
        "cargos/",
        CargoList.as_view(),
        name="list_cargos",
    ),
    path(
        "cargos/novo/",
        CargoCreate.as_view(),
        name="create_cargo",
    ),
    path(
        "cargos/<int:pk>/editar/",
        CargoUpdate.as_view(),
        name="update_cargo",
    ),
    path(
        "cargos/<int:pk>/excluir/",
        CargoDelete.as_view(),
        name="delete_cargo",
    ),

    path(
        "niveis/",
        NivelList.as_view(),
        name="list_niveis",
    ),
    path(
        "niveis/novo/",
        NivelCreate.as_view(),
        name="create_nivel",
    ),
    path(
        "niveis/<int:pk>/editar/",
        NivelUpdate.as_view(),
        name="update_nivel",
    ),
    path(
        "niveis/<int:pk>/excluir/",
        NivelDelete.as_view(),
        name="delete_nivel",
    ),

    path(
        "equipamentos/",
        EquipamentoList.as_view(),
        name="list_equipamentos",
    ),
    path(
        "equipamentos/novo/",
        EquipamentoCreate.as_view(),
        name="create_equipamento",
    ),
    path(
        "equipamentos/<int:pk>/editar/",
        EquipamentoUpdate.as_view(),
        name="update_equipamento",
    ),
    path(
        "equipamentos/<int:pk>/excluir/",
        EquipamentoDelete.as_view(),
        name="delete_equipamento",
    ),

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
    path(
        'acesso/<int:pk>/',
        gerenciar_acesso_funcionario,
        name='gerenciar_acesso_funcionario',
    ),
    path('delete/<int:pk>/', FuncionarioDelete.as_view(), name='delete_funcionario'),
    path('relatorio_funcionario', relatorio_funcionario, name='relatorio_funcionario'), # feito com reportlab
    path('relatorio_funcionario_html', Pdf.as_view(), name='relatorio_funcionario_html'),
    path('relatorio_funcionario_html_debug', PdfDebug.as_view(), name='relatorio_funcionario_html_debug'),
]
