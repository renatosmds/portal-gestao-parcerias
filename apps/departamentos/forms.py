from django import forms

from .models import Departamento


class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = [
            "nome",
            "tipo",
            "superior",
        ]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Informe o nome da unidade organizacional"
                    ),
                    "autocomplete": "organization-title",
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "superior": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

        queryset = Departamento.objects.none()

        if empresa:
            queryset = (
                Departamento.objects
                .filter(empresa=empresa)
                .order_by("tipo", "nome")
            )

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        self.fields["superior"].queryset = queryset
        self.fields["superior"].required = False
        self.fields["superior"].empty_label = (
            "Sem unidade superior"
        )

    def clean_nome(self):
        nome = (self.cleaned_data.get("nome") or "").strip()

        if not nome:
            raise forms.ValidationError(
                "Informe o nome da unidade organizacional."
            )

        queryset = Departamento.objects.filter(
            nome__iexact=nome
        )

        if self.empresa:
            queryset = queryset.filter(
                empresa=self.empresa
            )

        if self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise forms.ValidationError(
                "Ja existe uma unidade com esse nome "
                "nesta empresa."
            )

        return nome

    def clean(self):
        cleaned_data = super().clean()

        if self.empresa:
            self.instance.empresa = self.empresa

        self.instance.nome = (
            cleaned_data.get("nome")
            or self.instance.nome
        )

        self.instance.tipo = (
            cleaned_data.get("tipo")
            or self.instance.tipo
        )

        self.instance.superior = cleaned_data.get(
            "superior"
        )

        try:
            self.instance.clean()
        except Exception as exc:
            if hasattr(exc, "message_dict"):
                for campo, mensagens in exc.message_dict.items():
                    if campo in self.fields:
                        for mensagem in mensagens:
                            self.add_error(
                                campo,
                                mensagem,
                            )
                    else:
                        for mensagem in mensagens:
                            self.add_error(
                                None,
                                mensagem,
                            )
            else:
                raise

        return cleaned_data
