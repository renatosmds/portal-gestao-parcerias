from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Empresa


class EmpresaPermissaoMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True


class EmpresaEscopoMixin(LoginRequiredMixin):
    """
    Superusuários visualizam todas as empresas.

    Usuários comuns visualizam apenas a empresa vinculada ao próprio
    cadastro de funcionário.
    """

    def get_empresa_usuario(self):
        try:
            funcionario = self.request.user.funcionario
        except Exception:
            return None

        return getattr(funcionario, "empresa", None)

    def get_queryset(self):
        queryset = Empresa.objects.all().order_by("nome")

        if self.request.user.is_superuser:
            return queryset

        empresa = self.get_empresa_usuario()
        if not empresa:
            return queryset.none()

        return queryset.filter(pk=empresa.pk)
