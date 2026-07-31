from django import forms

from apps.lancamentos.models import Lancamento
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos

from .models import Documento


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            "descricao",
            "tipo",
            "numero_documento",
            "data_documento",
            "termo",
            "prestacao",
            "lancamento",
            "arquivo",
        ]
        widgets = {
            "data_documento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

        for field in self.fields.values():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.setdefault("class", "form-control-file")
            else:
                field.widget.attrs.setdefault("class", "form-control")

        termos = Termos.objects.order_by("termo", "numtermo")
        prestacoes = Prestacao.objects.order_by("numtermo", "credor")
        lancamentos = Lancamento.objects.order_by(
            "-data_documento",
            "-id",
        )

        if empresa:
            termos = termos.filter(empresa=empresa)
            prestacoes = prestacoes.filter(empresa=empresa)
            lancamentos = lancamentos.filter(empresa=empresa)

        self.fields["termo"].queryset = termos
        self.fields["prestacao"].queryset = prestacoes
        self.fields["lancamento"].queryset = lancamentos

    def clean(self):
        cleaned = super().clean()
        termo = cleaned.get("termo")
        prestacao = cleaned.get("prestacao")
        lancamento = cleaned.get("lancamento")

        if not termo and not prestacao and not lancamento:
            raise forms.ValidationError(
                "Vincule o documento a um termo, prestação ou lançamento."
            )

        return cleaned


class ConferenciaDocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = [
            "status",
            "documento_legivel",
            "dados_compativeis",
            "vigencia_valida",
            "pagamento_comprovado",
            "atesto_valido",
            "observacoes",
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "observacoes": forms.Textarea(
                attrs={"rows": 6, "class": "form-control"}
            ),
            "documento_legivel": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "dados_compativeis": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "vigencia_valida": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "pagamento_comprovado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
            "atesto_valido": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")
        observacoes = (cleaned.get("observacoes") or "").strip()

        if status in {
            Documento.Status.COM_PENDENCIA,
            Documento.Status.REPROVADO,
        } and not observacoes:
            self.add_error(
                "observacoes",
                "Descreva a pendência ou o motivo da reprovação.",
            )

        return cleaned
