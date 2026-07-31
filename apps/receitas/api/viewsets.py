from rest_framework.viewsets import ModelViewSet
from apps.receitas.models import Receitas
from .serializers import ReceitasSerializer


class ReceitasViewSet(ModelViewSet):
    queryset = Receitas.objects.all()
    serializer_class = ReceitasSerializer
