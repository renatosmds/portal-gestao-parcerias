from django import forms
from .models import Importacao


class ImportacaoUploadForm(forms.Form):
    tipo = forms.ChoiceField(choices=Importacao.Tipo.choices, label="Tipo de dados")
    sistema_origem = forms.CharField(max_length=80, required=False, initial="SIPCON / Planilha", label="Sistema de origem")
    arquivo = forms.FileField(label="Arquivo CSV ou Excel")

    def clean_arquivo(self):
        arquivo = self.cleaned_data["arquivo"]
        nome = arquivo.name.lower()
        if not nome.endswith((".csv", ".xlsx")):
            raise forms.ValidationError("Envie um arquivo CSV ou XLSX.")
        if arquivo.size > 10 * 1024 * 1024:
            raise forms.ValidationError("O arquivo deve ter no máximo 10 MB.")
        return arquivo
