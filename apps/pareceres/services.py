from copy import deepcopy

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.pareceres.models import ItemParecer, ParecerTecnico


MAPA_SEVERIDADE = {
    "informativa": ItemParecer.Severidade.INFORMATIVA,
    "informativo": ItemParecer.Severidade.INFORMATIVA,
    "info": ItemParecer.Severidade.INFORMATIVA,
    "alerta": ItemParecer.Severidade.ALERTA,
    "warning": ItemParecer.Severidade.ALERTA,
    "critica": ItemParecer.Severidade.CRITICA,
    "cr?tica": ItemParecer.Severidade.CRITICA,
    "critico": ItemParecer.Severidade.CRITICA,
    "cr?tico": ItemParecer.Severidade.CRITICA,
    "critical": ItemParecer.Severidade.CRITICA,
}


MAPA_CATEGORIA = {
    "documental": ItemParecer.Categoria.DOCUMENTAL,
    "documento": ItemParecer.Categoria.DOCUMENTAL,

    "financeira": ItemParecer.Categoria.FINANCEIRA,
    "financeiro": ItemParecer.Categoria.FINANCEIRA,

    "plano_trabalho": ItemParecer.Categoria.PLANO_TRABALHO,
    "plano de trabalho": ItemParecer.Categoria.PLANO_TRABALHO,
    "plano": ItemParecer.Categoria.PLANO_TRABALHO,

    "rh": ItemParecer.Categoria.RH,
    "recursos humanos": ItemParecer.Categoria.RH,

    "lgpd": ItemParecer.Categoria.LGPD,

    "vigencia": ItemParecer.Categoria.VIGENCIA,
    "vig?ncia": ItemParecer.Categoria.VIGENCIA,
}


def _normalizar(valor):
    return str(valor or "").strip().lower()


def severidade_para_item(valor):
    """
    Converte a severidade produzida pelo PGP Rules
    para o enum persistido no ItemParecer.

    Valor desconhecido nunca e promovido automaticamente
    para severidade critica.
    """
    return MAPA_SEVERIDADE.get(
        _normalizar(valor),
        ItemParecer.Severidade.ALERTA,
    )


def categoria_para_item(valor):
    """
    Converte a categoria do motor para o dominio
    persistido do parecer.
    """
    return MAPA_CATEGORIA.get(
        _normalizar(valor),
        ItemParecer.Categoria.OUTRA,
    )


def snapshot_resultado_regra(resultado):
    """
    Cria uma copia independente do resultado original.

    O snapshot deve sobreviver a futuras alteracoes
    no motor de regras ou na regra normativa.
    """
    if hasattr(resultado, "como_dict"):
        dados = resultado.como_dict()
    else:
        campos = (
            "codigo",
            "severidade",
            "titulo",
            "descricao",
            "regra",
            "categoria",
            "resultado",
            "fato_verificado",
            "evidencia",
            "fundamentacao",
            "risco_glosa",
            "recomendacao",
            "origem_normativa",
        )

        dados = {
            campo: getattr(resultado, campo, "")
            for campo in campos
        }

    return deepcopy(dados)


@transaction.atomic
def incorporar_resultado_regra(
    *,
    parecer,
    resultado,
    usuario,
    lancamento=None,
    documento=None,
    diligencia=None,
    ordem=0,
):
    """
    Incorpora um ResultadoRegra ao parecer como snapshot.

    Esta funcao NAO:
    - registra glosa;
    - altera Lancamento;
    - finaliza parecer;
    - conclui automaticamente por irregularidade;
    - substitui a manifestacao do analista.
    """

    if not isinstance(parecer, ParecerTecnico):
        raise ValidationError(
            "O parecer informado nao e um ParecerTecnico valido."
        )

    if usuario is None or not getattr(usuario, "pk", None):
        raise ValidationError(
            "A incorporacao do achado exige usuario responsavel."
        )

    dados = snapshot_resultado_regra(resultado)

    codigo_regra = str(
        dados.get("codigo")
        or getattr(resultado, "codigo", "")
        or ""
    )

    item = ItemParecer(
        parecer=parecer,

        # O codigo do ItemParecer fica livre.
        # codigo_regra identifica a regra que originou o achado.
        codigo="",
        codigo_regra=codigo_regra,

        categoria=categoria_para_item(
            dados.get("categoria")
        ),

        severidade=severidade_para_item(
            dados.get("severidade")
        ),

        origem=ItemParecer.Origem.PGP_RULES,

        titulo=str(
            dados.get("titulo")
            or "Achado do PGP Rules"
        ),

        descricao=str(
            dados.get("descricao")
            or ""
        ),

        fato_verificado=str(
            dados.get("fato_verificado")
            or ""
        ),

        evidencia=str(
            dados.get("evidencia")
            or ""
        ),

        fundamentacao=str(
            dados.get("fundamentacao")
            or ""
        ),

        risco_glosa=str(
            dados.get("risco_glosa")
            or ""
        ),

        recomendacao=str(
            dados.get("recomendacao")
            or ""
        ),

        resultado_origem=str(
            dados.get("resultado")
            or ""
        ),

        origem_normativa=str(
            dados.get("origem_normativa")
            or ""
        ),

        dados_origem=dados,

        lancamento=lancamento,
        documento=documento,
        diligencia=diligencia,

        ordem=ordem,
        criado_por=usuario,

        # Deliberadamente nao ha conclusao automatica.
        conclusao_item=ItemParecer.ConclusaoItem.NAO_ANALISADO,
        manifestacao_analista="",
    )

    # Importante: valida tambem segregacao por OSC/prestacao
    # implementada no model.
    item.full_clean()
    item.save()

    return item
