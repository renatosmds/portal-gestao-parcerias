from rest_framework.viewsets import ModelViewSet
from apps.prestacao.models import Prestacao
from .serializers import PrestacaoSerializer


class PrestacaoViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Prestacao.objects.all()
    serializer_class = PrestacaoSerializer
