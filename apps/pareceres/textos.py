from dataclasses import dataclass

from django.core.exceptions import ValidationError

from apps.pareceres.models import ItemParecer


@dataclass(frozen=True)
class TextoInconformidade:
    titulo: str
    texto: str
    pendencias: tuple[str, ...]
    possui_fato: bool
    possui_evidencia: bool
    possui_fundamentacao: bool
    possui_risco_glosa: bool

    @property
    def completo(self):
        return (
            self.possui_fato
            and self.possui_evidencia
            and self.possui_fundamentacao
        )


def _limpar(valor):
    return " ".join(
        str(valor or "").split()
    )


def _finalizar_frase(valor):
    texto = _limpar(valor)

    if not texto:
        return ""

    if texto.endswith((".", "!", "?", ";", ":")):
        return texto

    return texto + "."


def gerar_texto_inconformidade(item):
    """
    Gera rascunho estruturado de inconformidade
    a partir de um ItemParecer.

    Regras de seguranca:
    - nao inventa fundamentacao;
    - nao inventa evidencia;
    - nao presume irregularidade;
    - nao registra glosa;
    - nao altera o ItemParecer;
    - nao altera a conclusao do parecer;
    - nao substitui revisao humana.
    """

    if not isinstance(item, ItemParecer):
        raise ValidationError(
            "O item informado nao e um ItemParecer valido."
        )

    titulo = _limpar(item.titulo) or "Achado em an?lise"

    descricao = _finalizar_frase(item.descricao)
    fato = _finalizar_frase(item.fato_verificado)
    evidencia = _finalizar_frase(item.evidencia)
    fundamentacao = _finalizar_frase(item.fundamentacao)
    risco = _finalizar_frase(item.risco_glosa)

    pendencias = []

    if not fato:
        pendencias.append(
            "Fato verificado n?o informado."
        )

    if not evidencia:
        pendencias.append(
            "Evid?ncia n?o informada."
        )

    if not fundamentacao:
        pendencias.append(
            "Fundamenta??o normativa n?o informada."
        )

    blocos = []

    # O texto oficial come?a pelo fato quando dispon?vel.
    if fato:
        blocos.append(
            f"Foi identificado o seguinte fato: {fato}"
        )
    elif descricao:
        blocos.append(
            f"Foi registrado o seguinte achado: {descricao}"
        )
    else:
        blocos.append(
            "Foi registrado achado que necessita de an?lise t?cnica complementar."
        )

    if descricao and descricao != fato:
        blocos.append(
            f"Descri??o do achado: {descricao}"
        )

    if evidencia:
        blocos.append(
            f"Evid?ncia considerada: {evidencia}"
        )

    if fundamentacao:
        blocos.append(
            f"Fundamenta??o indicada: {fundamentacao}"
        )

    if risco:
        blocos.append(
            f"Risco identificado: {risco}"
        )

    texto = "\n\n".join(blocos)

    return TextoInconformidade(
        titulo=titulo,
        texto=texto,
        pendencias=tuple(pendencias),
        possui_fato=bool(fato),
        possui_evidencia=bool(evidencia),
        possui_fundamentacao=bool(fundamentacao),
        possui_risco_glosa=bool(risco),
    )



@dataclass(frozen=True)
class TextoRecomendacao:
    texto: str
    pendencias: tuple[str, ...]
    possui_recomendacao: bool
    possui_fundamentacao: bool
    possui_evidencia: bool
    requer_revisao_humana: bool = True

    @property
    def completo(self):
        return (
            self.possui_recomendacao
            and self.possui_fundamentacao
        )


def gerar_texto_recomendacao(item):
    """
    Gera rascunho estruturado de recomendacao
    a partir de um ItemParecer.

    Regras de seguranca:
    - nao inventa providencias;
    - nao determina glosa;
    - nao reprova despesa;
    - nao altera o item;
    - nao altera o parecer;
    - exige revisao humana.
    """

    if not isinstance(item, ItemParecer):
        raise ValidationError(
            "O item informado nao e um ItemParecer valido."
        )

    recomendacao = _finalizar_frase(
        item.recomendacao
    )

    fundamentacao = _finalizar_frase(
        item.fundamentacao
    )

    evidencia = _finalizar_frase(
        item.evidencia
    )

    pendencias = []

    if not recomendacao:
        pendencias.append(
            "Recomenda??o t?cnica n?o informada."
        )

    if not fundamentacao:
        pendencias.append(
            "Fundamenta??o normativa n?o informada."
        )

    blocos = []

    if recomendacao:
        blocos.append(
            f"Recomenda-se: {recomendacao}"
        )
    else:
        blocos.append(
            "Recomenda-se an?lise t?cnica complementar "
            "antes da defini??o de provid?ncia."
        )

    if fundamentacao:
        blocos.append(
            f"Fundamenta??o considerada: {fundamentacao}"
        )

    if evidencia:
        blocos.append(
            f"Evid?ncia relacionada: {evidencia}"
        )

    blocos.append(
        "A provid?ncia definitiva dever? ser validada "
        "pelo analista respons?vel."
    )

    return TextoRecomendacao(
        texto="\\n\\n".join(blocos),
        pendencias=tuple(pendencias),
        possui_recomendacao=bool(recomendacao),
        possui_fundamentacao=bool(fundamentacao),
        possui_evidencia=bool(evidencia),
        requer_revisao_humana=True,
    )
