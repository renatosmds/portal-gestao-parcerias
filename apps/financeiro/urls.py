from django.urls import path

from .views import (
    MovimentacaoFinanceiraCreate,
    MovimentacaoFinanceiraDelete,
    MovimentacaoFinanceiraList,
    MovimentacaoFinanceiraUpdate,
    competencias_financeiro,
    confirmar_conciliacao_financeira,
    prestacoes_financeiro,
    rejeitar_conciliacao_financeira,
    termos_financeiro,
)


urlpatterns = [
    path(
        "",
        MovimentacaoFinanceiraList.as_view(),
        name="list_movimentacoes_financeiras",
    ),
    path(
        "novo/",
        MovimentacaoFinanceiraCreate.as_view(),
        name="create_movimentacao_financeira",
    ),
    path(
        "<int:pk>/editar/",
        MovimentacaoFinanceiraUpdate.as_view(),
        name="update_movimentacao_financeira",
    ),
    path(
        "<int:pk>/excluir/",
        MovimentacaoFinanceiraDelete.as_view(),
        name="delete_movimentacao_financeira",
    ),
    path(
        "<int:movimentacao_id>/conciliar/"
        "<int:lancamento_id>/",
        confirmar_conciliacao_financeira,
        name="confirmar_conciliacao_financeira",
    ),
    path(
        "<int:movimentacao_id>/rejeitar/"
        "<int:lancamento_id>/",
        rejeitar_conciliacao_financeira,
        name="rejeitar_conciliacao_financeira",
    ),
    path(
        "ajax/termos/",
        termos_financeiro,
        name="financeiro_termos",
    ),
    path(
        "ajax/prestacoes/",
        prestacoes_financeiro,
        name="financeiro_prestacoes",
    ),
    path(
        "ajax/competencias/",
        competencias_financeiro,
        name="financeiro_competencias",
    ),
]
