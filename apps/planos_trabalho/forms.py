from django import forms

from apps.metas.models import MetaExecucao
from apps.termos.models import Termos

from .escopo import (
    metas_permitidas,
    planos_permitidos,
    termos_permitidos,
)
from .models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)


class PlanoTrabalhoForm(forms.ModelForm):

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

        if user is None:
            self.fields[
                "termo"
            ].queryset = Termos.objects.none()

            self.fields[
                "versao_anterior"
            ].queryset = PlanoTrabalho.objects.none()

            return

        self.fields[
            "termo"
        ].queryset = termos_permitidos(
            user
        )

        anteriores = planos_permitidos(
            user
        )

        if self.instance.pk:
            anteriores = anteriores.exclude(
                pk=self.instance.pk
            )

        termo_id = None

        if self.is_bound:
            termo_id = self.data.get(
                "termo"
            )
        elif self.instance.pk:
            termo_id = (
                self.instance.termo_id
            )

        if termo_id:
            anteriores = anteriores.filter(
                termo_id=termo_id
            )

        self.fields[
            "versao_anterior"
        ].queryset = anteriores

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

    def __init__(
        self,
        *args,
        user=None,
        plano=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        if plano is None and self.instance.pk:
            plano = self.instance.plano

        if user is None or plano is None:
            self.fields[
                "meta"
            ].queryset = MetaExecucao.objects.none()
            return

        self.fields[
            "meta"
        ].queryset = metas_permitidas(
            user,
            plano=plano,
        )

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
