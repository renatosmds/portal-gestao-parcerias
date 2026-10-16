from django import forms

from apps.core.acesso import filtrar_por_empresa

from .models import (
    Funcionario,
    RegimeBancoHoras,
)


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(
        self,
        attrs=None,
        format=None,
    ):
        super().__init__(
            attrs=attrs,
            format=format or "%Y-%m-%d",
        )


class RegimeBancoHorasForm(forms.ModelForm):
    """
    Cadastro do instrumento/regime que autoriza e disciplina
    a compensacao ou o Banco de Horas do colaborador.
    """

    class Meta:
        model = RegimeBancoHoras

        fields = [
            "funcionario",
            "tipo",
            "data_inicio",
            "data_fim",
            "prazo_compensacao_meses",
            "tratamento_vencimento",
            "fundamento",
            "referencia_documento",
            "ativo",
        ]

        widgets = {
            "data_inicio": DateInput(),
            "data_fim": DateInput(),
            "fundamento": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                }
            ),
            "referencia_documento": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "Ex.: Acordo individual de 01/11/2026, "
                        "ACT 2026/2027 ou CCT aplicavel"
                    ),
                }
            ),
        }

        labels = {
            "funcionario": "Colaborador",
            "tipo": "Modalidade",
            "data_inicio": "Inicio da vigencia",
            "data_fim": "Fim da vigencia",
            "prazo_compensacao_meses": (
                "Prazo de compensacao (meses)"
            ),
            "tratamento_vencimento": (
                "Tratamento no vencimento"
            ),
            "fundamento": "Fundamento",
            "referencia_documento": (
                "Referencia do acordo / ACT / CCT"
            ),
            "ativo": "Regime ativo",
        }

    def __init__(
        self,
        *args,
        user=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        funcionarios = (
            Funcionario.objects
            .select_related("empresa")
            .order_by("nome")
        )

        if user:
            funcionarios = filtrar_por_empresa(
                funcionarios,
                user,
            )
        else:
            funcionarios = funcionarios.none()

        # Preserva na edicao um colaborador eventualmente
        # inativo, desde que esteja no escopo permitido.
        if (
            self.instance
            and self.instance.pk
            and self.instance.funcionario_id
        ):
            funcionarios = (
                funcionarios
                .filter(
                    pk=self.instance.funcionario_id
                )
                | funcionarios.filter(
                    ativo=True
                )
            )

            funcionarios = (
                funcionarios
                .distinct()
                .order_by("nome")
            )
        else:
            funcionarios = (
                funcionarios
                .filter(ativo=True)
            )

        self.fields[
            "funcionario"
        ].queryset = funcionarios

        for nome, campo in self.fields.items():

            if nome == "ativo":
                campo.widget.attrs.setdefault(
                    "class",
                    "form-check-input",
                )

            elif isinstance(
                campo.widget,
                forms.CheckboxInput,
            ):
                campo.widget.attrs.setdefault(
                    "class",
                    "form-check-input",
                )

            else:
                classes = (
                    campo.widget.attrs
                    .get(
                        "class",
                        "",
                    )
                    .split()
                )

                if "form-control" not in classes:
                    classes.append(
                        "form-control"
                    )

                campo.widget.attrs[
                    "class"
                ] = " ".join(classes)

    def clean(self):
        cleaned = super().clean()

        inicio = cleaned.get(
            "data_inicio"
        )

        fim = cleaned.get(
            "data_fim"
        )

        if (
            inicio
            and fim
            and fim < inicio
        ):
            self.add_error(
                "data_fim",
                (
                    "O fim da vigencia nao pode "
                    "ser anterior ao inicio."
                ),
            )

        return cleaned
