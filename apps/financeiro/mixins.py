from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)

from apps.core.acesso import filtrar_por_empresa


class MovimentacaoFinanceiraPermissaoMixin(
    LoginRequiredMixin,
    PermissionRequiredMixin,
):
    raise_exception = True


class MovimentacaoFinanceiraEscopoMixin:
    def get_queryset(self):
        queryset = super().get_queryset()

        return filtrar_por_empresa(
            queryset,
            self.request.user,
            campo="empresa",
        )
