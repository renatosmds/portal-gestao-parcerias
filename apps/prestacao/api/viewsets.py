from rest_framework.viewsets import ModelViewSet
from apps.prestacao.models import Prestacao
from .serializers import PrestacaoSerializer


class PrestacaoViewSet(ModelViewSet):
    queryset = Prestacao.objects.all()
    serializer_class = PrestacaoSerializer
