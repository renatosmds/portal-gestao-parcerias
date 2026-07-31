from rest_framework.viewsets import ModelViewSet
from apps.parcerias.models import Parcerias
from .serializers import ParceriasSerializer


class ParceriasViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Parcerias.objects.all()
    serializer_class = ParceriasSerializer
