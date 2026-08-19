from dataclasses import dataclass

from django.core.exceptions import ValidationError

from apps.diligencias.models import Diligencia
from apps.pareceres.models import ItemParecer, ParecerTecnico


STATUS_DILIGENCIA_ABERTA = {
    Diligencia.Status.RASCUNHO,
    Diligencia.Status.ENVIADA,
    Diligencia.Status.VISUALIZADA,
    Diligencia.Status.EM_RESPOSTA,
    Diligencia.Status.RESPONDIDA,
    Diligencia.Status.REANALISE,
}


@dataclass(frozen=True)
class ResultadoClassificacaoParecer:
    classificacao_sugerida: str
    total_itens: int
    regulares: int
    sanados: int
    ressalvas: int
    pendencias_saneaveis: int
    irregularidades: int
    nao_sanados: int
    nao_analisados: int
    diligencias_abertas: int
    justificativa: str
    requer_revisao_humana: bool = True


def classificar_parecer_tecnicamente(parecer):
    """
    Consolida os itens do parecer e produz somente
    uma SUGESTAO de classificacao tecnica.

    Esta funcao NAO:
    - altera ParecerTecnico.tipo_conclusao;
    - finaliza o parecer;
    - registra glosa;
    - reprova prestacao de contas;
    - substitui decisao humana.
    """

    if not isinstance(parecer, ParecerTecnico):
        raise ValidationError(
            "O objeto informado nao e um ParecerTecnico valido."
        )

    if not parecer.pk:
        raise ValidationError(
            "O parecer deve estar salvo antes da classificacao."
        )

    itens = list(
        parecer.itens.select_related(
            "diligencia"
        ).all()
    )

    total = len(itens)

    contadores = {
        "regulares": 0,
        "sanados": 0,
        "ressalvas": 0,
        "pendencias_saneaveis": 0,
        "irregularidades": 0,
        "nao_sanados": 0,
        "nao_analisados": 0,
        "diligencias_abertas": 0,
    }

    for item in itens:

        conclusao = item.conclusao_item

        if conclusao == ItemParecer.ConclusaoItem.REGULAR:
            contadores["regulares"] += 1

        elif conclusao == ItemParecer.ConclusaoItem.SANADO:
            contadores["sanados"] += 1

        elif conclusao == ItemParecer.ConclusaoItem.RESSALVA:
            contadores["ressalvas"] += 1

        elif conclusao == ItemParecer.ConclusaoItem.PENDENCIA_SANEAVEL:
            contadores["pendencias_saneaveis"] += 1

        elif conclusao == ItemParecer.ConclusaoItem.IRREGULARIDADE:
            contadores["irregularidades"] += 1

        elif conclusao == ItemParecer.ConclusaoItem.NAO_SANADO:
            contadores["nao_sanados"] += 1

        elif conclusao == ItemParecer.ConclusaoItem.NAO_ANALISADO:
            contadores["nao_analisados"] += 1

        if (
            item.diligencia_id
            and item.diligencia.status
            in STATUS_DILIGENCIA_ABERTA
        ):
            contadores["diligencias_abertas"] += 1

    # Ordem de precedencia deliberadamente conservadora.
    if total == 0:
        classificacao = (
            ParecerTecnico.TipoConclusao.INCONCLUSIVO
        )
        justificativa = (
            "O parecer ainda nao possui itens de analise."
        )

    elif (
        contadores["irregularidades"] > 0
        or contadores["nao_sanados"] > 0
    ):
        classificacao = (
            ParecerTecnico.TipoConclusao.COM_IRREGULARIDADES
        )
        justificativa = (
            "Existem itens classificados como irregularidade "
            "ou pendencias nao sanadas."
        )

    elif contadores["diligencias_abertas"] > 0:
        classificacao = (
            ParecerTecnico.TipoConclusao.AGUARDANDO_DILIGENCIA
        )
        justificativa = (
            "Existem diligencias ainda abertas ou em reanalise."
        )

    elif contadores["pendencias_saneaveis"] > 0:
        classificacao = (
            ParecerTecnico.TipoConclusao.COM_PENDENCIAS_SANEAVEIS
        )
        justificativa = (
            "Existem pendencias classificadas como saneaveis."
        )

    elif contadores["ressalvas"] > 0:
        classificacao = (
            ParecerTecnico.TipoConclusao.COM_RESSALVAS
        )
        justificativa = (
            "Existem itens classificados com ressalva."
        )

    elif contadores["nao_analisados"] > 0:
        classificacao = (
            ParecerTecnico.TipoConclusao.EM_ANALISE
        )
        justificativa = (
            "Ainda existem itens sem conclusao tecnica."
        )

    else:
        classificacao = (
            ParecerTecnico.TipoConclusao.SEM_PENDENCIAS_RELEVANTES
        )
        justificativa = (
            "Todos os itens possuem conclusao regular "
            "ou foram saneados."
        )

    return ResultadoClassificacaoParecer(
        classificacao_sugerida=classificacao,
        total_itens=total,
        justificativa=justificativa,
        requer_revisao_humana=True,
        **contadores,
    )
