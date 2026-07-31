from django.forms import ModelForm
from .models import Curso

class CursoForm(ModelForm):
    class Meta:
        model = Curso
        fields = ['nomeCurso', 'anoCurso', 'mesCurso', 'cronograma', 'horario', 'carga', 'docente', 'ementa', 'obs',
                  'certificado', 'documento']
