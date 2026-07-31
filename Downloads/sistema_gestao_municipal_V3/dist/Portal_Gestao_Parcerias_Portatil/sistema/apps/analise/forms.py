from django import forms

from apps.prestacao.models import Prestacao
from apps.termos.models import Termos

from .models import Analise


class AnaliseForm(forms.ModelForm):
    class Meta:
        model = Analise
        fields = [
            "numtermo",
            "prestacao",
            "nomeOSC",
            "numRA",
            "item",
            "inconformidade",
            "recomendacoes",
            "posicaoSecretaria",
            "status",
            "concluida",
        ]
        widgets = {
            "numtermo": forms.Select(attrs={"class": "form-control"}),
            "prestacao": forms.Select(attrs={"class": "form-control"}),
            "nomeOSC": forms.TextInput(attrs={"class": "form-control"}),
            "numRA": forms.TextInput(attrs={"class": "form-control"}),
            "item": forms.TextInput(attrs={"class": "form-control"}),
            "inconformidade": forms.Textarea(
                attrs={"class": "form-control", "rows": 6}
            ),
            "recomendacoes": forms.Textarea(
                attrs={"class": "form-control", "rows": 6}
            ),
            "posicaoSecretaria": forms.Textarea(
                attrs={"class": "form-control", "rows": 5}
            ),
            "status": forms.TextInput(attrs={"class": "form-control"}),
            "concluida": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

        termos = Termos.objects.order_by("termo", "numtermo")
        prestacoes = Prestacao.objects.order_by("numtermo", "credor")

        if empresa:
            termos = termos.filter(empresa=empresa)
            prestacoes = prestacoes.filter(empresa=empresa)

        self.fields["numtermo"].queryset = termos
        self.fields["prestacao"].queryset = prestacoes

    def clean(self):
        cleaned = super().clean()
        termo = cleaned.get("numtermo")
        prestacao = cleaned.get("prestacao")
        item = (cleaned.get("item") or "").strip()
        inconformidade = (cleaned.get("inconformidade") or "").strip()
        recomendacoes = (cleaned.get("recomendacoes") or "").strip()

        if not termo and not prestacao:
            raise forms.ValidationError(
                "Informe o termo ou a prestação de contas relacionada."
            )

        if not inconformidade and not recomendacoes:
            raise forms.ValidationError(
                "Informe ao menos a inconformidade ou a recomendação."
            )

        if termo and item:
            queryset = Analise.objects.filter(
                numtermo=termo,
                item__iexact=item,
            )
            if self.empresa:
                queryset = queryset.filter(empresa=self.empresa)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError(
                    "Já existe uma análise para este item do termo."
                )

        return cleaned
