from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .services import get_empresa_do_usuario


class EmpresaAtualMixin(LoginRequiredMixin):
    @property
    def empresa_atual(self):
        if not hasattr(self, "_empresa_atual"):
            self._empresa_atual = None if self.request.user.is_superuser else get_empresa_do_usuario(self.request.user)
        return self._empresa_atual


class FuncionarioPorEmpresaMixin(EmpresaAtualMixin):
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(empresa=self.empresa_atual)


class PermissaoFuncionarioMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True

    def has_permission(self):
        if self.request.user.is_superuser:
            return True
        return super().has_permission()
