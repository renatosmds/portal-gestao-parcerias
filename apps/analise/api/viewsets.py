from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.analise.models import Analise

from .serializers import AnaliseSerializer


from apps.core.acesso import empresa_do_usuario, usuario_pode_ver_todas_empresas
class AnaliseViewSet(ModelViewSet):
    serializer_class = AnaliseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Analise.objects.select_related(
            "empresa",
            "numtermo",
            "prestacao",
        )

        if usuario_pode_ver_todas_empresas(self.request.user):
            return queryset

        try:
            empresa = empresa_do_usuario(self.request.user)
        except Exception:
            return queryset.none()

        return queryset.filter(empresa=empresa)

    def perform_create(self, serializer):
        if usuario_pode_ver_todas_empresas(self.request.user):
            empresa_id = self.request.data.get("empresa")
            serializer.save(empresa_id=empresa_id)
            return

        serializer.save(empresa=empresa_do_usuario(self.request.user))
