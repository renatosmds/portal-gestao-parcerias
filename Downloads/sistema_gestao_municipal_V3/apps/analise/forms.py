from django.forms import ModelForm
from .models import Analise


class AnaliseForm(ModelForm):
    class Meta:
        model = Analise
        fields = ['numtermo', 'nomeOSC', 'numRA', 'item', 'inconformidade', 'recomendacoes', 'posicaoSecretaria',
                  'status'
                  ]
