from django.core.exceptions import ValidationError
from django.db import transaction

from .models import PlanoTrabalho


def plano_aplicavel_em(
    termo,
    data_referencia,
):
    """
    Retorna a versão mais recente do Plano de Trabalho
    aplicável na data informada.

    Versões em rascunho ou canceladas são ignoradas.
    """

    if not termo or not data_referencia:
        return None

    planos = (
        PlanoTrabalho.objects
        .filter(
            termo=termo,
            situacao__in=[
                PlanoTrabalho.Situacao.VIGENTE,
                PlanoTrabalho.Situacao.SUBSTITUIDO,
            ],
        )
        .order_by("-versao")
    )

    for plano in planos:
        if plano.aplicavel_em(
            data_referencia
        ):
            return plano

    return None


@transaction.atomic
def ativar_versao(plano):
    """
    Ativa uma versão e preserva o histórico.

    As versões atualmente vigentes do mesmo Termo
    são marcadas como substituídas antes da ativação
    da nova versão.
    """

    plano.full_clean()

    PlanoTrabalho.objects.filter(
        termo=plano.termo,
        situacao=PlanoTrabalho.Situacao.VIGENTE,
    ).exclude(
        pk=plano.pk
    ).update(
        situacao=PlanoTrabalho.Situacao.SUBSTITUIDO
    )

    plano.situacao = (
        PlanoTrabalho.Situacao.VIGENTE
    )

    plano.full_clean()
    plano.save(
        update_fields=[
            "situacao",
            "atualizado_em",
        ]
    )

    return plano


def validar_cadeia_versoes(termo):
    """
    Verificação estrutural da cadeia de versões.
    Não altera os registros.
    """

    planos = list(
        PlanoTrabalho.objects
        .filter(termo=termo)
        .select_related("versao_anterior")
        .order_by("versao")
    )

    problemas = []

    vistos = set()

    for plano in planos:

        if plano.versao in vistos:
            problemas.append(
                {
                    "codigo": "PT_VERSAO_DUPLICADA",
                    "plano_id": plano.pk,
                }
            )

        vistos.add(plano.versao)

        if (
            plano.versao_anterior
            and plano.versao_anterior.termo_id
            != termo.pk
        ):
            problemas.append(
                {
                    "codigo": "PT_CADEIA_TERMO_DIVERGENTE",
                    "plano_id": plano.pk,
                }
            )

        if (
            plano.versao_anterior
            and plano.versao
            <= plano.versao_anterior.versao
        ):
            problemas.append(
                {
                    "codigo": "PT_CADEIA_ORDEM_INVALIDA",
                    "plano_id": plano.pk,
                }
            )

    return problemas
