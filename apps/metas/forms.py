from django import forms
from .models import MetaExecucao
from apps.core.acesso import filtrar_por_empresa
from apps.prestacao.models import Prestacao


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

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Prestacao.objects.select_related("empresa")
        self.fields["prestacao"].queryset = filtrar_por_empresa(qs, user) if user else qs.none()
