from rest_framework.serializers import ModelSerializer
from apps.curso.models import Curso


class CursoSerializer(ModelSerializer):
    class Meta:
        model = Curso
        fields = ['nomeCurso', 'anoCurso', 'mesCurso', 'cronograma', 'horario', 'carga', 'docente', 'ementa', 'obs',
                  'certificado', 'documento'
                  ]
