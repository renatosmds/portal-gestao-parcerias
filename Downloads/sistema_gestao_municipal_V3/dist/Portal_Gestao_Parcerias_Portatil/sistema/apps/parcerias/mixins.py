from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import Parcerias


class ParceriaPermissaoMixin(LoginRequiredMixin, PermissionRequiredMixin):
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


class ParceriaEscopoMixin(LoginRequiredMixin):
    def get_empresa_usuario(self):
        try:
            funcionario = self.request.user.funcionario
        except Exception:
            return None
        return getattr(funcionario, "empresa", None)

    def get_queryset(self):
        queryset = Parcerias.objects.select_related(
            "empresa",
            "numtermo",
            "credor",
        )

        if self.request.user.is_superuser:
            return queryset

        empresa = self.get_empresa_usuario()
        if not empresa:
            return queryset.none()

        return queryset.filter(empresa=empresa)
