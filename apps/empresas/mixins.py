from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from apps.core.acesso import filtrar_por_empresa

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
    """Aplica o escopo multiempresa definido pela politica central de acesso."""

    def get_queryset(self):
        queryset = Empresa.objects.all().order_by("nome")
        return filtrar_por_empresa(
            queryset,
            self.request.user,
            campo="pk",
        )
