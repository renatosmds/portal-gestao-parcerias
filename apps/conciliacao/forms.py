from django import forms
from apps.lancamentos.models import Lancamento
from .models import Conciliacao, Movimentacao, OcorrenciaConciliacao, VinculoConciliacao


class ConciliacaoForm(forms.ModelForm):
    class Meta:
        model = Conciliacao
        fields = ["prestacao", "saldo_inicial", "saldo_final_informado", "observacoes"]
        widgets = {"observacoes": forms.Textarea(attrs={"rows": 3})}


class ImportacaoExtratoForm(forms.Form):
    arquivo = forms.FileField(help_text="Formatos aceitos: CSV, XLSX e OFX.")

    def clean_arquivo(self):
        arquivo = self.cleaned_data["arquivo"]
        ext = arquivo.name.lower().rsplit(".", 1)[-1]
        if ext not in {"csv", "xlsx", "ofx"}:
            raise forms.ValidationError("Use um arquivo CSV, XLSX ou OFX.")
        return arquivo


class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ["data", "descricao", "documento", "favorecido", "tipo", "categoria", "valor", "saldo_apos"]
        widgets = {"data": forms.DateInput(attrs={"type": "date"})}


class VinculoForm(forms.ModelForm):
    class Meta:
        model = VinculoConciliacao
        fields = ["lancamento", "valor", "observacao"]

    def __init__(self, *args, prestacao=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Lancamento.objects.select_related("fornecedor").order_by("data_pagamento", "numero_lancamento")
        if prestacao:
            qs = qs.filter(prestacao=prestacao)
        self.fields["lancamento"].queryset = qs


class IgnorarMovimentacaoForm(forms.Form):
    justificativa = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), min_length=10)


class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = OcorrenciaConciliacao
        fields = ["situacao", "justificativa"]
        widgets = {"justificativa": forms.Textarea(attrs={"rows": 3})}
