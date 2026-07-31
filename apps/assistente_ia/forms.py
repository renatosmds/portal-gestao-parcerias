from django import forms

from .models import ProcessamentoAssistido


class RevisaoProcessamentoForm(forms.ModelForm):
    class Meta:
        model = ProcessamentoAssistido
        fields = ["decisao_revisor", "observacoes_revisor"]
        widgets = {
            "decisao_revisor": forms.Select(attrs={"class": "form-control"}),
            "observacoes_revisor": forms.Textarea(
                attrs={"class": "form-control", "rows": 5}
            ),
        }
