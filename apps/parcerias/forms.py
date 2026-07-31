from django import forms

from apps.fornecedores.models import Fornecedores

from .models import Parcerias


class DateInput(forms.DateInput):
    input_type = "date"


class ParceriasForm(forms.ModelForm):
    class Meta:
        model = Parcerias
        fields = [
            "numtermo",
            "nomeOSC",
            "credor",
            "fileTC",
            "numRA",
            "numOficioRA",
            "fileRA",
            "fileOficioRA",
            "dtRaSMDS",
            "respRA",
            "numRE",
            "numOficioRE",
            "fileRE",
            "fileOficioRE",
            "dtReSMDS",
            "respRE",
            "fileRRE",
            "prazoFinal",
            "status",
            "prazoDecorrido",
            "prazoRestante",
            "historico",
            "concluido",
            "photo",
        ]
        widgets = {
            "numtermo": forms.Select(attrs={"class": "form-control"}),
            "nomeOSC": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome da organização da sociedade civil",
                }
            ),
            "credor": forms.Select(attrs={"class": "form-control"}),
            "fileTC": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
            "numRA": forms.TextInput(attrs={"class": "form-control"}),
            "numOficioRA": forms.TextInput(attrs={"class": "form-control"}),
            "fileRA": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
            "fileOficioRA": forms.ClearableFileInput(
                attrs={"class": "form-control-file"}
            ),
            "dtRaSMDS": DateInput(attrs={"class": "form-control"}),
            "respRA": forms.TextInput(attrs={"class": "form-control"}),
            "numRE": forms.TextInput(attrs={"class": "form-control"}),
            "numOficioRE": forms.TextInput(attrs={"class": "form-control"}),
            "fileRE": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
            "fileOficioRE": forms.ClearableFileInput(
                attrs={"class": "form-control-file"}
            ),
            "dtReSMDS": DateInput(attrs={"class": "form-control"}),
            "respRE": forms.TextInput(attrs={"class": "form-control"}),
            "fileRRE": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
            "prazoFinal": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex.: 30/11/2026",
                }
            ),
            "status": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Situação atual da parceria",
                }
            ),
            "prazoDecorrido": forms.TextInput(attrs={"class": "form-control"}),
            "prazoRestante": forms.TextInput(attrs={"class": "form-control"}),
            "historico": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Registre o histórico relevante",
                }
            ),
            "concluido": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

        fornecedores = Fornecedores.objects.order_by("credor")
        if empresa:
            fornecedores = fornecedores.filter(empresa=empresa)

        self.fields["credor"].queryset = fornecedores

    def clean_nomeOSC(self):
        nome = (self.cleaned_data.get("nomeOSC") or "").strip()
        if not nome:
            raise forms.ValidationError("Informe o nome da OSC.")
        return nome

    def clean(self):
        cleaned = super().clean()
        termo = cleaned.get("numtermo")
        osc = cleaned.get("nomeOSC")

        if termo and osc:
            queryset = Parcerias.objects.filter(
                numtermo=termo,
                nomeOSC__iexact=osc,
            )
            if self.empresa:
                queryset = queryset.filter(empresa=self.empresa)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError(
                    "Já existe uma parceria com este termo e esta OSC na empresa."
                )

        return cleaned
