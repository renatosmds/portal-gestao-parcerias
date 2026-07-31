from django import forms
from .models import MetaExecucao


class MetaExecucaoForm(forms.ModelForm):
    class Meta:
        model = MetaExecucao
        fields = ["prestacao", "codigo", "titulo", "descricao", "unidade", "valor_previsto", "valor_realizado", "inicio", "fim", "situacao", "responsavel", "justificativa"]
        widgets = {
            "inicio": forms.DateInput(attrs={"type": "date"}),
            "fim": forms.DateInput(attrs={"type": "date"}),
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "justificativa": forms.Textarea(attrs={"rows": 3}),
        }
