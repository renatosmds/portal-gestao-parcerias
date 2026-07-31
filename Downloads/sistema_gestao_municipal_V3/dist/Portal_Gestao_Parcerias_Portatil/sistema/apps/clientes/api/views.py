from rest_framework.viewsets import ModelViewSet
from apps.clientes.models import Clientes
from .serializers import ClientesSerializer


class ClientesViewSet(ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer
