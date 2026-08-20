from dataclasses import dataclass

from django.core.exceptions import ValidationError

from apps.pareceres.classificacao import (
    classificar_parecer_tecnicamente,
)
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)


@dataclass(frozen=True)
class ConclusaoExecutivaParecer:
    classificacao_sugerida: str
    titulo: str
    resumo_executivo: str
    pendencias_relevantes: tuple
    aspectos_regulares: tuple
    diligencias_pendentes: int
    itens_criticos: int
    itens_alerta: int
    itens_informativos: int
    requer_revisao_humana: bool = True


def _limpar(valor):
    return " ".join(
        str(valor or "").split()
    )


def _identificador_item(item):
    return (
        _limpar(item.codigo)
        or _limpar(item.codigo_regra)
        or f"ITEM-{item.pk}"
    )


def _rotulo_item(item):
    codigo = _identificador_item(item)
    titulo = _limpar(item.titulo)

    if titulo:
        return f"{codigo} - {titulo}"

    return codigo


def _texto_classificacao(classificacao):
    mapa = {
        ParecerTecnico.TipoConclusao.EM_ANALISE:
            "O parecer permanece em análise técnica.",

        ParecerTecnico.TipoConclusao.SEM_PENDENCIAS_RELEVANTES:
            (
                "Não foram identificadas pendências relevantes "
                "entre os itens já concluídos."
            ),

        ParecerTecnico.TipoConclusao.COM_RESSALVAS:
            (
                "Foram identificados itens que recomendam "
                "registro de ressalvas."
            ),

        ParecerTecnico.TipoConclusao.COM_PENDENCIAS_SANEAVEIS:
            (
                "Foram identificadas pendências passíveis "
                "de saneamento."
            ),

        ParecerTecnico.TipoConclusao.COM_IRREGULARIDADES:
            (
                "Foram identificados itens classificados como "
                "irregularidade ou pendências não sanadas."
            ),

        ParecerTecnico.TipoConclusao.AGUARDANDO_DILIGENCIA:
            (
                "A análise possui diligências ainda pendentes "
                "de conclusão."
            ),

        ParecerTecnico.TipoConclusao.INCONCLUSIVO:
            (
                "Os elementos disponíveis ainda não permitem "
                "conclusão técnica consolidada."
            ),
    }

    return mapa.get(
        classificacao,
        "O parecer requer análise técnica complementar.",
    )


def gerar_conclusao_executiva(parecer):
    """
    Gera minuta executiva consolidada do parecer.

    A função NÃO:
    - altera o parecer;
    - grava tipo_conclusao;
    - finaliza o parecer;
    - registra glosa;
    - aprova ou reprova a prestação de contas.
    """

    if not isinstance(parecer, ParecerTecnico):
        raise ValidationError(
            "O objeto informado não é um ParecerTecnico válido."
        )

    if not parecer.pk:
        raise ValidationError(
            "O parecer deve estar salvo."
        )

    classificacao = classificar_parecer_tecnicamente(
        parecer
    )

    itens = list(
        parecer.itens.select_related(
            "diligencia"
        ).all()
    )

    pendencias = []
    regulares = []

    itens_criticos = 0
    itens_alerta = 0
    itens_informativos = 0

    for item in itens:

        if item.severidade == ItemParecer.Severidade.CRITICA:
            itens_criticos += 1

        elif item.severidade == ItemParecer.Severidade.ALERTA:
            itens_alerta += 1

        elif item.severidade == ItemParecer.Severidade.INFORMATIVA:
            itens_informativos += 1

        rotulo = _rotulo_item(item)

        if item.conclusao_item in {
            ItemParecer.ConclusaoItem.IRREGULARIDADE,
            ItemParecer.ConclusaoItem.NAO_SANADO,
            ItemParecer.ConclusaoItem.PENDENCIA_SANEAVEL,
            ItemParecer.ConclusaoItem.RESSALVA,
            ItemParecer.ConclusaoItem.NAO_ANALISADO,
        }:
            pendencias.append(rotulo)

        elif item.conclusao_item in {
            ItemParecer.ConclusaoItem.REGULAR,
            ItemParecer.ConclusaoItem.SANADO,
        }:
            regulares.append(rotulo)

    texto_classificacao = _texto_classificacao(
        classificacao.classificacao_sugerida
    )

    partes = [
        (
            f"Foram analisados {classificacao.total_itens} "
            "item(ns) no parecer técnico."
        ),
        texto_classificacao,
    ]

    if classificacao.diligencias_abertas:
        partes.append(
            (
                f"Há {classificacao.diligencias_abertas} "
                "diligência(s) ainda aberta(s) ou em reanálise."
            )
        )

    if classificacao.nao_sanados:
        partes.append(
            (
                f"Há {classificacao.nao_sanados} "
                "pendência(s) registrada(s) como não sanada(s)."
            )
        )

    if classificacao.irregularidades:
        partes.append(
            (
                f"Há {classificacao.irregularidades} "
                "item(ns) classificado(s) como irregularidade."
            )
        )

    if classificacao.ressalvas:
        partes.append(
            (
                f"Há {classificacao.ressalvas} "
                "item(ns) classificado(s) com ressalva."
            )
        )

    if classificacao.pendencias_saneaveis:
        partes.append(
            (
                f"Há {classificacao.pendencias_saneaveis} "
                "pendência(s) classificada(s) como saneável(is)."
            )
        )

    partes.append(
        (
            "A presente conclusão possui caráter de minuta "
            "técnica e deverá ser revisada e validada pelo "
            "analista responsável antes de qualquer decisão "
            "administrativa definitiva."
        )
    )

    return ConclusaoExecutivaParecer(
        classificacao_sugerida=(
            classificacao.classificacao_sugerida
        ),
        titulo="Conclusão executiva preliminar",
        resumo_executivo=" ".join(partes),
        pendencias_relevantes=tuple(pendencias),
        aspectos_regulares=tuple(regulares),
        diligencias_pendentes=(
            classificacao.diligencias_abertas
        ),
        itens_criticos=itens_criticos,
        itens_alerta=itens_alerta,
        itens_informativos=itens_informativos,
        requer_revisao_humana=True,
    )
