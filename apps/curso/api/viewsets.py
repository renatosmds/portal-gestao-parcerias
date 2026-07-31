from rest_framework.viewsets import ModelViewSet
from apps.curso.models import Curso
from .serializers import CursoSerializer


class CursoViewSet(ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
