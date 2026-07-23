from django import forms

from .models import Fornecedores


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedores
        fields = [
            "credor",
            "pessoa",
            "razao",
            "tipo",
            "numero",
            "fantasia",
            "endereco",
            "bairro",
            "cep",
            "cidade",
            "estado",
            "email",
            "telefone",
            "iestadual",
            "imunicipal",
        ]
        widgets = {
            "credor": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome do fornecedor ou credor",
                }
            ),
            "pessoa": forms.Select(attrs={"class": "form-control"}),
            "razao": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Razão social",
                }
            ),
            "tipo": forms.Select(attrs={"class": "form-control"}),
            "numero": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "CPF ou CNPJ",
                }
            ),
            "fantasia": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nome fantasia",
                }
            ),
            "endereco": forms.TextInput(attrs={"class": "form-control"}),
            "bairro": forms.TextInput(attrs={"class": "form-control"}),
            "cep": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "iestadual": forms.TextInput(attrs={"class": "form-control"}),
            "imunicipal": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

    def clean_credor(self):
        credor = (self.cleaned_data.get("credor") or "").strip()
        if not credor:
            raise forms.ValidationError("Informe o nome do fornecedor ou credor.")
        return credor

    def clean_numero(self):
        numero = (self.cleaned_data.get("numero") or "").strip()

        if not numero:
            return numero

        queryset = Fornecedores.objects.filter(numero__iexact=numero)

        if self.empresa:
            queryset = queryset.filter(empresa=self.empresa)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "Já existe um fornecedor com este CPF/CNPJ nesta empresa."
            )

        return numero
