from django import forms

from apps.pareceres.models import ItemParecer, ParecerTecnico
from apps.prestacao.models import Prestacao
from apps.pareceres.escopo import (
    empresa_do_usuario,
    usuario_acesso_global,
)


def _aplicar_classes_bootstrap(form):
    for field in form.fields.values():
        widget = field.widget

        classe = widget.attrs.get(
            "class",
            "",
        )

        if isinstance(
            widget,
            forms.Select,
        ):
            nova_classe = "form-control"
        else:
            nova_classe = "form-control"

        widget.attrs["class"] = (
            f"{classe} {nova_classe}".strip()
        )




class ParecerCriacaoForm(forms.Form):

    prestacao = forms.ModelChoiceField(
        queryset=Prestacao.objects.none(),
        label="Presta??o de contas",
    )

    numero = forms.CharField(
        required=False,
        max_length=50,
        label="N?mero do parecer",
        help_text=(
            "Opcional. Se n?o informado, "
            "o PGP gerar? uma identifica??o."
        ),
    )

    def __init__(
        self,
        *args,
        user=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        qs = (
            Prestacao.objects
            .select_related(
                "empresa",
                "termo",
            )
            .order_by(
                "empresa__nome",
                "numtermo",
                "pk",
            )
        )

        if not usuario_acesso_global(user):
            empresa = empresa_do_usuario(user)

            if empresa is None:
                qs = qs.none()
            else:
                qs = qs.filter(
                    empresa=empresa
                )

        # A cria??o inicial deve aparecer apenas
        # para presta??es que ainda n?o possuem parecer.
        qs = qs.filter(
            pareceres_tecnicos__isnull=True
        ).distinct()

        self.fields[
            "prestacao"
        ].queryset = qs

        _aplicar_classes_bootstrap(self)


class ParecerRevisaoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_classes_bootstrap(self)

    class Meta:
        model = ParecerTecnico
        fields = [
            "tipo_conclusao",
            "resumo_executivo",
            "fundamentacao_geral",
            "conclusao",
            "ressalvas",
            "recomendacoes_gerais",
        ]
        widgets = {
            "resumo_executivo": forms.Textarea(
                attrs={"rows": 5}
            ),
            "fundamentacao_geral": forms.Textarea(
                attrs={"rows": 5}
            ),
            "conclusao": forms.Textarea(
                attrs={"rows": 5}
            ),
            "ressalvas": forms.Textarea(
                attrs={"rows": 4}
            ),
            "recomendacoes_gerais": forms.Textarea(
                attrs={"rows": 4}
            ),
        }
        labels = {
            "tipo_conclusao": "Conclusão técnica do analista",
            "resumo_executivo": "Resumo executivo revisado",
            "fundamentacao_geral": "Fundamentação geral",
            "conclusao": "Conclusão",
            "ressalvas": "Ressalvas",
            "recomendacoes_gerais": "Recomendações gerais",
        }


class ItemParecerRevisaoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _aplicar_classes_bootstrap(self)

    class Meta:
        model = ItemParecer
        fields = [
            "fato_verificado",
            "evidencia",
            "fundamentacao",
            "risco_glosa",
            "recomendacao",
            "manifestacao_analista",
            "conclusao_item",
        ]
        widgets = {
            "fato_verificado": forms.Textarea(
                attrs={"rows": 4}
            ),
            "evidencia": forms.Textarea(
                attrs={"rows": 4}
            ),
            "fundamentacao": forms.Textarea(
                attrs={"rows": 4}
            ),
            "risco_glosa": forms.Textarea(
                attrs={"rows": 3}
            ),
            "recomendacao": forms.Textarea(
                attrs={"rows": 4}
            ),
            "manifestacao_analista": forms.Textarea(
                attrs={"rows": 5}
            ),
        }
        labels = {
            "fato_verificado": "Fato verificado",
            "evidencia": "Evidência",
            "fundamentacao": "Fundamentação",
            "risco_glosa": "Risco de glosa",
            "recomendacao": "Recomendação",
            "manifestacao_analista": "Manifestação do analista",
            "conclusao_item": "Conclusão humana do item",
        }
