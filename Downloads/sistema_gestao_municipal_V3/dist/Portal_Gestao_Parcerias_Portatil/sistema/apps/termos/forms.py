from django import forms

from .models import Termos


class TermosForm(forms.ModelForm):
    class Meta:
        model = Termos
        fields = [
            "nomeosc", "numtermo", "numpa", "vigencia", "assinatura",
            "valorglobal", "valorrepasse", "valorsaldo", "parcelasAbertas",
            "numdispensa", "nomemunicipio", "nomeintermediario",
            "nomesecretario", "nomerepresentante", "tipo", "termo",
            "apelido", "parceria", "objeto", "relatoriosDeSinteses",
            "inicioVigencia", "terminoVigencia", "analista", "status",
            "saldoDashboard", "saldoContaSinteseDespesas", "rendimento",
            "saldoContaSinteseMovFinanceira", "valorDevolvido", "saldoFinal",
            "totalDeLacamentos", "lacamentosRegulares",
            "lacamentosIrregulares", "lacamentosGlosados",
            "lacamentosNaoEnviados", "naoanalisados", "total",
            "extratosBancarios", "pendenciasOfx", "valoresGlosados",
            "glosasRestituidas", "saldoGlosas", "observacoes",
            "fileOficio", "fileTermo", "filePlanoTrabalho", "fileEmpenho",
            "fileNap", "fileAtesto", "fileCertidao", "fileOficioFia",
        ]
        widgets = {
            "assinatura": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "observacoes": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.ClearableFileInput)):
                field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()
        termo = (cleaned.get("termo") or "").strip()
        numtermo = (cleaned.get("numtermo") or "").strip()

        if not termo and not numtermo:
            raise forms.ValidationError("Informe o Termo ou o Nº Termo.")

        queryset = Termos.objects.all()
        if self.empresa:
            queryset = queryset.filter(empresa=self.empresa)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if termo and queryset.filter(termo__iexact=termo).exists():
            raise forms.ValidationError("Já existe um termo com essa identificação nesta empresa.")

        return cleaned
