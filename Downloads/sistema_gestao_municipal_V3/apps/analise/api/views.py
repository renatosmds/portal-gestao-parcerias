from rest_framework.viewsets import ModelViewSet
from apps.analise.models import Analise
from .serializers import AnaliseSerializer


class AnaliseViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Analise.objects.all()
    serializer_class = AnaliseSerializer
