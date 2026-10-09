from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import Analise


from apps.core.acesso import empresa_do_usuario, usuario_pode_ver_todas_empresas
class AnalisePermissaoMixin(LoginRequiredMixin, PermissionRequiredMixin):
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


class AnaliseEscopoMixin(LoginRequiredMixin):
    def get_empresa_usuario(self):
        try:
            return empresa_do_usuario(self.request.user)
        except Exception:
            return None

    def get_queryset(self):
        queryset = Analise.objects.select_related(
            "empresa",
            "numtermo",
            "prestacao",
        )

        if usuario_pode_ver_todas_empresas(self.request.user):
            return queryset

        empresa = self.get_empresa_usuario()
        if not empresa:
            return queryset.none()

        return queryset.filter(empresa=empresa)
