from django import forms

from .models import Prestacao


class PrestacaoForm(forms.ModelForm):
    class Meta:
        model = Prestacao
        fields = [
            'tipoTermo',
            'numtermo',
            'termoAditivo',
            'credor',
            'numCredor',
            'tipo',
            'CpfCnpj',
            'oficioCcoaf',
            'sco',
            'agCredito',
            'ccCredito',
            'uo',
            'funcao',
            'subfuncao',
            'programa',
            'projeto',
            'natureza',
            'fonte',
            'cod_reduz',
            'bancoCredor',
            'agCredor',
            'ccCredor',
            'gestora',
            'matricula',
            'contato',
            'valorContrato',
            'qtdParcelas',
            'mesParcela1',
            'anoParcela1',
            'valorParcela1',
            'empenhoParcela1',
            'napParcela1',
            'dataNapParcela1',
            'mesParcela2',
            'anoParcela2',
            'valorParcela2',
            'empenhoParcela2',
            'napParcela2',
            'dataNapParcela2',
            'mesParcela3',
            'anoParcela3',
            'valorParcela3',
            'empenhoParcela3',
            'napParcela3',
            'dataNapParcela3',
            'mesParcela4',
            'anoParcela4',
            'valorParcela4',
            'empenhoParcela4',
            'napParcela4',
            'dataNapParcela4',
            'mesParcela5',
            'anoParcela5',
            'valorParcela5',
            'empenhoParcela5',
            'napParcela5',
            'dataNapParcela5',
            'mesParcela6',
            'anoParcela6',
            'valorParcela6',
            'empenhoParcela6',
            'napParcela6',
            'dataNapParcela6',
            'mesParcela7',
            'anoParcela7',
            'valorParcela7',
            'empenhoParcela7',
            'napParcela7',
            'dataNapParcela7',
            'mesParcela8',
            'anoParcela8',
            'valorParcela8',
            'empenhoParcela8',
            'napParcela8',
            'dataNapParcela8',
            'mesParcela9',
            'anoParcela9',
            'valorParcela9',
            'empenhoParcela9',
            'napParcela9',
            'dataNapParcela9',
            'mesParcela10',
            'anoParcela10',
            'valorParcela10',
            'empenhoParcela10',
            'napParcela10',
            'dataNapParcela10',
            'mesParcela11',
            'anoParcela11',
            'valorParcela11',
            'empenhoParcela11',
            'napParcela11',
            'dataNapParcela11',
            'mesParcela12',
            'anoParcela12',
            'valorParcela12',
            'empenhoParcela12',
            'napParcela12',
            'dataNapParcela12',
            'concluida'
        ]

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.setdefault("class", "form-control-file")
            else:
                field.widget.attrs.setdefault("class", "form-control")

        for name, field in self.fields.items():
            if name.startswith("dataNap"):
                field.widget = forms.DateInput(
                    attrs={"type": "date", "class": "form-control"}
                )

    def clean(self):
        cleaned = super().clean()
        numero = (cleaned.get("numtermo") or "").strip()
        credor = (cleaned.get("credor") or "").strip()

        if not numero and not credor:
            raise forms.ValidationError(
                "Informe o número do termo ou o credor."
            )

        queryset = Prestacao.objects.all()

        if self.empresa:
            queryset = queryset.filter(empresa=self.empresa)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if numero and queryset.filter(numtermo__iexact=numero).exists():
            raise forms.ValidationError(
                "Já existe uma prestação com esse número de termo nesta empresa."
            )

        return cleaned


class MovimentarPrestacaoForm(forms.Form):
    nova_situacao = forms.ChoiceField(label="Nova situação", choices=Prestacao.SituacaoWorkflow.choices, widget=forms.Select(attrs={"class":"form-control"}))
    observacao = forms.CharField(label="Observação / justificativa", required=False, widget=forms.Textarea(attrs={"class":"form-control", "rows":4}))

    def __init__(self, *args, situacoes_permitidas=None, **kwargs):
        super().__init__(*args, **kwargs)
        if situacoes_permitidas is not None:
            self.fields["nova_situacao"].choices = [(v, l) for v,l in Prestacao.SituacaoWorkflow.choices if v in situacoes_permitidas]
