from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import Documento


class DocumentoPermissaoMixin(LoginRequiredMixin, PermissionRequiredMixin):
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


class DocumentoEscopoMixin(LoginRequiredMixin):
    def get_empresa_usuario(self):
        try:
            return self.request.user.funcionario.empresa
        except Exception:
            return None

    def get_queryset(self):
        queryset = Documento.objects.select_related(
            "empresa",
            "termo",
            "prestacao",
            "lancamento",
            "conferido_por",
        )

        if self.request.user.is_superuser:
            return queryset

        empresa = self.get_empresa_usuario()
        if not empresa:
            return queryset.none()

        return queryset.filter(empresa=empresa)
