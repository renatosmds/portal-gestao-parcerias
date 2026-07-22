from django.contrib.auth.mixins import LoginRequiredMixin

from .services import get_empresa_do_usuario


class EmpresaAtualMixin(LoginRequiredMixin):
    """
    Disponibiliza a empresa do usuário autenticado para as views do módulo.
    """

    @property
    def empresa_atual(self):
        if not hasattr(self, "_empresa_atual"):
            self._empresa_atual = get_empresa_do_usuario(self.request.user)
        return self._empresa_atual


class FuncionarioPorEmpresaMixin(EmpresaAtualMixin):
    """
    Restringe qualquer consulta de Funcionario à empresa autenticada.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(empresa=self.empresa_atual)
