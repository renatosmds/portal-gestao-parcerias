from decimal import Decimal

from django import forms

from apps.analise.models import Analise
from apps.fornecedores.models import Fornecedores
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos

from .models import Lancamento


class LancamentoForm(forms.ModelForm):
    class Meta:
        model = Lancamento
        fields = [
            "termo",
            "prestacao",
            "fornecedor",
            "analise",
            "numero_lancamento",
            "tipo_documento",
            "numero_documento",
            "chave_acesso",
            "data_documento",
            "data_pagamento",
            "descricao",
            "valor_documento",
            "valor_glosa",
            "situacao",
            "atestado",
            "justificativa",
            "recomendacao",
            "documento",
            "comprovante_pagamento",
        ]
        widgets = {
            "data_documento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "data_pagamento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "justificativa": forms.Textarea(
                attrs={"rows": 5, "class": "form-control"}
            ),
            "recomendacao": forms.Textarea(
                attrs={"rows": 5, "class": "form-control"}
            ),
            "atestado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.setdefault("class", "form-control-file")
            else:
                field.widget.attrs.setdefault("class", "form-control")

        termos = Termos.objects.order_by("termo", "numtermo")
        prestacoes = Prestacao.objects.order_by("numtermo", "credor")
        fornecedores = Fornecedores.objects.order_by(
            "credor",
            "razao",
            "fantasia",
        )
        analises = Analise.objects.order_by("-atualizada_em")

        if empresa:
            termos = termos.filter(empresa=empresa)
            prestacoes = prestacoes.filter(empresa=empresa)
            fornecedores = fornecedores.filter(empresa=empresa)
            analises = analises.filter(empresa=empresa)

        self.fields["termo"].queryset = termos
        self.fields["prestacao"].queryset = prestacoes
        self.fields["fornecedor"].queryset = fornecedores
        self.fields["analise"].queryset = analises

    def clean(self):
        cleaned = super().clean()
        numero = (cleaned.get("numero_lancamento") or "").strip()
        valor_documento = cleaned.get("valor_documento") or Decimal("0.00")
        valor_glosa = cleaned.get("valor_glosa") or Decimal("0.00")
        situacao = cleaned.get("situacao")
        justificativa = (cleaned.get("justificativa") or "").strip()
        recomendacao = (cleaned.get("recomendacao") or "").strip()

        queryset = Lancamento.objects.all()
        if self.empresa:
            queryset = queryset.filter(empresa=self.empresa)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if numero and queryset.filter(numero_lancamento__iexact=numero).exists():
            raise forms.ValidationError(
                "Já existe um lançamento com esse número nesta empresa."
            )

        if valor_glosa > valor_documento:
            self.add_error(
                "valor_glosa",
                "A glosa não pode ser maior que o valor do documento.",
            )

        if situacao == Lancamento.Situacao.GLOSADO and valor_glosa <= 0:
            self.add_error(
                "valor_glosa",
                "Informe um valor de glosa maior que zero.",
            )

        if situacao in {
            Lancamento.Situacao.RESSALVA,
            Lancamento.Situacao.REPROVADO,
            Lancamento.Situacao.GLOSADO,
        } and not justificativa:
            self.add_error(
                "justificativa",
                "Informe a justificativa ou inconformidade.",
            )

        if situacao in {
            Lancamento.Situacao.RESSALVA,
            Lancamento.Situacao.REPROVADO,
            Lancamento.Situacao.GLOSADO,
        } and not recomendacao:
            self.add_error(
                "recomendacao",
                "Informe a recomendação correspondente.",
            )

        return cleaned
