from django import forms

from .models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)


class PlanoTrabalhoForm(forms.ModelForm):

    class Meta:
        model = PlanoTrabalho
        fields = [
            "termo",
            "versao",
            "titulo",
            "versao_anterior",
            "origem",
            "situacao",
            "data_eficacia",
            "instrumento_alteracao",
            "justificativa_alteracao",
            "inicio_vigencia",
            "fim_vigencia",
            "data_aprovacao",
            "arquivo",
            "observacoes",
        ]

        widgets = {
            "inicio_vigencia": forms.DateInput(
                attrs={"type": "date"}
            ),
            "fim_vigencia": forms.DateInput(
                attrs={"type": "date"}
            ),
            "data_aprovacao": forms.DateInput(
                attrs={"type": "date"}
            ),
            "data_eficacia": forms.DateInput(
                attrs={"type": "date"}
            ),
            "justificativa_alteracao": forms.Textarea(
                attrs={"rows": 3}
            ),
            "observacoes": forms.Textarea(
                attrs={"rows": 3}
            ),
        }


class ItemPlanoTrabalhoForm(forms.ModelForm):

    class Meta:
        model = ItemPlanoTrabalho
        fields = [
            "codigo",
            "rubrica_nivel_1",
            "rubrica_nivel_2",
            "rubrica_nivel_3",
            "descricao",
            "unidade",
            "quantidade_prevista",
            "valor_unitario_previsto",
            "valor_total_previsto",
            "inicio_execucao",
            "fim_execucao",
            "meta",
            "ativo",
            "observacoes",
        ]

        widgets = {
            "inicio_execucao": forms.DateInput(
                attrs={"type": "date"}
            ),
            "fim_execucao": forms.DateInput(
                attrs={"type": "date"}
            ),
            "observacoes": forms.Textarea(
                attrs={"rows": 3}
            ),
        }

