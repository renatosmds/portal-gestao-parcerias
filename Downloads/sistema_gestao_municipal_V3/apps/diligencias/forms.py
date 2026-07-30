from django import forms
from .models import ComentarioInterno, Diligencia, RespostaDiligencia


class DiligenciaForm(forms.ModelForm):
    class Meta:
        model = Diligencia
        fields = ["assunto", "descricao", "fundamento", "prioridade", "prazo_resposta", "empresa", "prestacao", "lancamento", "documento", "funcionario", "responsavel"]
        widgets = {"prazo_resposta": forms.DateInput(attrs={"type": "date"}), "descricao": forms.Textarea(attrs={"rows": 5}), "fundamento": forms.Textarea(attrs={"rows": 3})}


class RespostaDiligenciaForm(forms.ModelForm):
    class Meta:
        model = RespostaDiligencia
        fields = ["texto", "anexo"]
        widgets = {"texto": forms.Textarea(attrs={"rows": 5})}


class ComentarioInternoForm(forms.ModelForm):
    class Meta:
        model = ComentarioInterno
        fields = ["texto"]
        widgets = {"texto": forms.Textarea(attrs={"rows": 3})}
