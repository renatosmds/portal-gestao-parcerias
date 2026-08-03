from django import forms

from .models import ChamadoSuporte, InteracaoChamado


class ChamadoSuporteForm(forms.ModelForm):
    class Meta:
        model = ChamadoSuporte
        fields = ["assunto", "categoria", "prioridade", "descricao", "pagina_origem", "anexo"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 6}),
            "pagina_origem": forms.HiddenInput(),
        }


class InteracaoChamadoForm(forms.ModelForm):
    class Meta:
        model = InteracaoChamado
        fields = ["mensagem"]
        widgets = {"mensagem": forms.Textarea(attrs={"rows": 4, "placeholder": "Escreva sua resposta..."})}
