from django.forms import ModelForm
from .models import Conferencia3


class Conferencia3Form(ModelForm):
    def __init__(self, user, Funcionario=None, *args, **kwargs):
        super(Conferencia3Form, self).__init__(*args, **kwargs)
        self.fields['funcionario'].queryset = Funcionario.objects.filter(
            empresa=user.funcionario.empresa)


    class Meta:
        model = Conferencia3
        fields = ['numtermo', 'parcela', 'ordem', 'rubricaNivel1', 'rubricaNivel2', 'rubricaNivel3', 'credor',
                  'tipo', 'CpfCnpj', 'especie', 'numero', 'data', 'comprovante', 'valor', 'fileBoleto', 'fileNF',
                  'fileComprPag', 'fileOrcamentos', 'photo', 'conferido', 'notificado', 'aprovado', 'notificacao',
                  ]
