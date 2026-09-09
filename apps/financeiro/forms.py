from django import forms

from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos

from .models import MovimentacaoFinanceira


class MovimentacaoFinanceiraForm(forms.ModelForm):

    class Meta:
        model = MovimentacaoFinanceira
        fields = [
            "termo",
            "prestacao",
            "competencia",
            "data",
            "tipo",
            "valor",
            "descricao",
            "documento",
            "observacao",
        ]
        widgets = {
            "data": forms.DateInput(
                attrs={"type": "date"}
            ),
            "valor": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "observacao": forms.Textarea(
                attrs={"rows": 4}
            ),
        }

    def __init__(
        self,
        *args,
        empresa=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.empresa = empresa

        self.fields["termo"].queryset = (
            Termos.objects.none()
        )

        self.fields["prestacao"].queryset = (
            Prestacao.objects.none()
        )

        self.fields["competencia"].queryset = (
            CompetenciaPrestacao.objects.none()
        )

        if not empresa:
            return

        self.fields["termo"].queryset = (
            Termos.objects
            .filter(empresa=empresa)
            .order_by("numtermo")
        )

        termo_id = (
            self.data.get("termo")
            if self.is_bound
            else getattr(
                self.instance,
                "termo_id",
                None,
            )
        )

        if termo_id:
            self.fields["prestacao"].queryset = (
                Prestacao.objects
                .filter(
                    empresa=empresa,
                    termo_id=termo_id,
                )
                .order_by("numtermo")
            )

        prestacao_id = (
            self.data.get("prestacao")
            if self.is_bound
            else getattr(
                self.instance,
                "prestacao_id",
                None,
            )
        )

        if prestacao_id:
            self.fields["competencia"].queryset = (
                CompetenciaPrestacao.objects
                .filter(
                    prestacao_id=prestacao_id,
                    prestacao__empresa=empresa,
                )
                .order_by("-ano", "-mes")
            )

    def clean(self):
        cleaned_data = super().clean()

        termo = cleaned_data.get("termo")
        prestacao = cleaned_data.get("prestacao")
        competencia = cleaned_data.get("competencia")

        if not self.empresa:
            raise forms.ValidationError(
                "Empresa n?o definida para a movimenta??o."
            )

        if termo and termo.empresa_id != self.empresa.pk:
            self.add_error(
                "termo",
                "O termo n?o pertence ? empresa selecionada.",
            )

        if prestacao:
            if prestacao.empresa_id != self.empresa.pk:
                self.add_error(
                    "prestacao",
                    "A presta??o n?o pertence ? empresa selecionada.",
                )

            if termo and prestacao.termo_id != termo.pk:
                self.add_error(
                    "prestacao",
                    "A presta??o n?o pertence ao termo selecionado.",
                )

        if competencia:
            if not prestacao:
                self.add_error(
                    "competencia",
                    "Selecione a presta??o antes da compet?ncia.",
                )
            elif competencia.prestacao_id != prestacao.pk:
                self.add_error(
                    "competencia",
                    "A compet?ncia n?o pertence ? presta??o selecionada.",
                )

        return cleaned_data
