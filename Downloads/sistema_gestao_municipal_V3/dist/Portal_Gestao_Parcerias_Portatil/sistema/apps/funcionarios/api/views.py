from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from apps.funcionarios.api.serializers import FuncionarioSerializer
from apps.funcionarios.models import Funcionario
from apps.funcionarios.services import get_empresa_do_usuario


class FuncionarioViewSet(viewsets.ModelViewSet):
    """API de funcionários isolada pela empresa do usuário autenticado."""

    serializer_class = FuncionarioSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_queryset(self):
        empresa = get_empresa_do_usuario(self.request.user)
        return Funcionario.objects.filter(empresa=empresa).order_by("nome")

    def perform_create(self, serializer):
        """Impede que o cliente da API escolha outra empresa."""
        empresa = get_empresa_do_usuario(self.request.user)
        serializer.save(empresa=empresa)
