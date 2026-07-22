from rest_framework.viewsets import ModelViewSet
from apps.termos.models import Termos
from .serializers import TermosSerializer


class TermosViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Termos.objects.all()
    serializer_class = TermosSerializer