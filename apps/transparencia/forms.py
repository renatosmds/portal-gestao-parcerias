from django import forms
from .models import PublicacaoDocumento, PublicacaoParceria


class PublicacaoParceriaForm(forms.ModelForm):
    class Meta:
        model = PublicacaoParceria
        fields = ["publicada", "orgao_responsavel", "resumo_publico", "motivo_restricao"]
        widgets = {
            "resumo_publico": forms.Textarea(attrs={"rows": 4}),
            "motivo_restricao": forms.Textarea(attrs={"rows": 3}),
        }


class PublicacaoDocumentoForm(forms.ModelForm):
    class Meta:
        model = PublicacaoDocumento
        fields = [
            "classificacao",
            "publicado",
            "titulo_publico",
            "descricao_publica",
            "motivo_restricao",
        ]
        widgets = {
            "descricao_publica": forms.Textarea(attrs={"rows": 3}),
            "motivo_restricao": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("publicado") and cleaned.get("classificacao") != PublicacaoDocumento.Classificacao.PUBLICO:
            self.add_error("publicado", "Somente documentos classificados como Públicos podem ser publicados.")
        return cleaned
