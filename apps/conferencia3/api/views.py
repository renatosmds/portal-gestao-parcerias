from rest_framework.viewsets import ModelViewSet
from apps.conferencia3.models import Conferencia3
from .serializers import Conferencia3Serializer


class Conferencia3ViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Conferencia3.objects.all()
    serializer_class = Conferencia3Serializer
