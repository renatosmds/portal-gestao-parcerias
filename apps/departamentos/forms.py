from django import forms

from .models import Departamento


class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ["nome"]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Informe o nome do departamento",
                    "autocomplete": "organization-title",
                }
            )
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_nome(self):
        nome = (self.cleaned_data.get("nome") or "").strip()

        if not nome:
            raise forms.ValidationError("Informe o nome do departamento.")

        queryset = Departamento.objects.filter(nome__iexact=nome)

        if self.empresa:
            queryset = queryset.filter(empresa=self.empresa)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "Já existe um departamento com esse nome nesta empresa."
            )

        return nome
