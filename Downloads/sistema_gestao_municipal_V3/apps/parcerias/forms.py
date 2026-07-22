from django.forms import ModelForm
from .models import Parcerias


class ParceriasForm(ModelForm):
    class Meta:
        model = Parcerias
        fields = ['numtermo', 'nomeOSC', 'fileTC', 'numRA', 'numOficioRA', 'fileRA', 'fileOficioRA', 'dtRaSMDS',
                  'respRA', 'numRE', 'numOficioRE', 'fileRE', 'fileOficioRE', 'dtReSMDS', 'respRE', 'fileRRE',
                  'prazoFinal', 'status', 'prazoDecorrido', 'prazoRestante', 'historico', 'concluido', 'photo'
                  ]
