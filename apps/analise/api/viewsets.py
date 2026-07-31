from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.analise.models import Analise

from .serializers import AnaliseSerializer


class AnaliseViewSet(ModelViewSet):
    serializer_class = AnaliseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Analise.objects.select_related(
            "empresa",
            "numtermo",
            "prestacao",
        )

        if self.request.user.is_superuser:
            return queryset

        try:
            empresa = self.request.user.funcionario.empresa
        except Exception:
            return queryset.none()

        return queryset.filter(empresa=empresa)

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            empresa_id = self.request.data.get("empresa")
            serializer.save(empresa_id=empresa_id)
            return

        serializer.save(empresa=self.request.user.funcionario.empresa)
