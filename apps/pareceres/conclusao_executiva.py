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
            "O parecer permanece em an?lise t?cnica.",

        ParecerTecnico.TipoConclusao.SEM_PENDENCIAS_RELEVANTES:
            (
                "N?o foram identificadas pend?ncias relevantes "
                "entre os itens j? conclu?dos."
            ),

        ParecerTecnico.TipoConclusao.COM_RESSALVAS:
            (
                "Foram identificados itens que recomendam "
                "registro de ressalvas."
            ),

        ParecerTecnico.TipoConclusao.COM_PENDENCIAS_SANEAVEIS:
            (
                "Foram identificadas pend?ncias pass?veis "
                "de saneamento."
            ),

        ParecerTecnico.TipoConclusao.COM_IRREGULARIDADES:
            (
                "Foram identificados itens classificados como "
                "irregularidade ou pend?ncias n?o sanadas."
            ),

        ParecerTecnico.TipoConclusao.AGUARDANDO_DILIGENCIA:
            (
                "A an?lise possui dilig?ncias ainda pendentes "
                "de conclus?o."
            ),

        ParecerTecnico.TipoConclusao.INCONCLUSIVO:
            (
                "Os elementos dispon?veis ainda n?o permitem "
                "conclus?o t?cnica consolidada."
            ),
    }

    return mapa.get(
        classificacao,
        "O parecer requer an?lise t?cnica complementar.",
    )


def gerar_conclusao_executiva(parecer):
    """
    Gera minuta executiva consolidada do parecer.

    A fun??o N?O:
    - altera o parecer;
    - grava tipo_conclusao;
    - finaliza o parecer;
    - registra glosa;
    - aprova ou reprova a presta??o de contas.
    """

    if not isinstance(parecer, ParecerTecnico):
        raise ValidationError(
            "O objeto informado n?o ? um ParecerTecnico v?lido."
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
            "item(ns) no parecer t?cnico."
        ),
        texto_classificacao,
    ]

    if classificacao.diligencias_abertas:
        partes.append(
            (
                f"H? {classificacao.diligencias_abertas} "
                "dilig?ncia(s) ainda aberta(s) ou em rean?lise."
            )
        )

    if classificacao.nao_sanados:
        partes.append(
            (
                f"H? {classificacao.nao_sanados} "
                "pend?ncia(s) registrada(s) como n?o sanada(s)."
            )
        )

    if classificacao.irregularidades:
        partes.append(
            (
                f"H? {classificacao.irregularidades} "
                "item(ns) classificado(s) como irregularidade."
            )
        )

    if classificacao.ressalvas:
        partes.append(
            (
                f"H? {classificacao.ressalvas} "
                "item(ns) classificado(s) com ressalva."
            )
        )

    if classificacao.pendencias_saneaveis:
        partes.append(
            (
                f"H? {classificacao.pendencias_saneaveis} "
                "pend?ncia(s) classificada(s) como sane?vel(is)."
            )
        )

    partes.append(
        (
            "A presente conclus?o possui car?ter de minuta "
            "t?cnica e dever? ser revisada e validada pelo "
            "analista respons?vel antes de qualquer decis?o "
            "administrativa definitiva."
        )
    )

    return ConclusaoExecutivaParecer(
        classificacao_sugerida=(
            classificacao.classificacao_sugerida
        ),
        titulo="Conclus?o executiva preliminar",
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
