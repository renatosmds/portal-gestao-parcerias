from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import Empresa


class EmpresaPermissaoMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Permite acesso integral ao superusuário e aplica permissões aos demais."""

    def has_permission(self):
        if self.request.user.is_superuser:
            return True
        return super().has_permission()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        raise PermissionDenied(
            "Seu perfil não possui permissão para acessar este recurso."
        )


class EmpresaEscopoMixin(LoginRequiredMixin):
    """Superusuários veem todas as OSCs; usuários comuns, apenas a vinculada."""

    def get_empresa_usuario(self):
        funcionario = getattr(self.request.user, "funcionario", None)
        return getattr(funcionario, "empresa", None) if funcionario else None

    def get_queryset(self):
        queryset = Empresa.objects.all().order_by("nome")
        if self.request.user.is_superuser:
            return queryset
        empresa = self.get_empresa_usuario()
        return queryset.filter(pk=empresa.pk) if empresa else queryset.none()
