from rest_framework.viewsets import ModelViewSet
from apps.clientes.models import Clientes
from .serializers import ClientesSerializer


class ClientesViewSet(ModelViewSet):
    queryset = Clientes.objects.all()
    serializer_class = ClientesSerializer
