from copy import deepcopy

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q


from apps.documentos.models import Documento
from apps.lancamentos.models import Lancamento
from apps.regras.engine import motor_regras
from apps.pareceres.models import ItemParecer, ParecerTecnico


MAPA_SEVERIDADE = {
    "informativa": ItemParecer.Severidade.INFORMATIVA,
    "informativo": ItemParecer.Severidade.INFORMATIVA,
    "info": ItemParecer.Severidade.INFORMATIVA,
    "alerta": ItemParecer.Severidade.ALERTA,
    "warning": ItemParecer.Severidade.ALERTA,
    "critica": ItemParecer.Severidade.CRITICA,
    "crítica": ItemParecer.Severidade.CRITICA,
    "critico": ItemParecer.Severidade.CRITICA,
    "crítico": ItemParecer.Severidade.CRITICA,
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
    "vigência": ItemParecer.Categoria.VIGENCIA,
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



def _resultados_do_motor(resultado_motor):
    """
    Normaliza os formatos de retorno do PGP Rules.

    - analisar_documento retorna uma colecao de ResultadoRegra;
    - analisar_lancamento retorna ResultadoAnaliseLancamento,
      cujos resultados ficam em .achados.
    """

    if resultado_motor is None:
        return []

    if hasattr(
        resultado_motor,
        "achados",
    ):
        return list(
            resultado_motor.achados
            or []
        )

    if isinstance(
        resultado_motor,
        (list, tuple, set),
    ):
        return list(
            resultado_motor
        )

    try:
        return list(
            iter(resultado_motor)
        )
    except TypeError:
        return [
            resultado_motor
        ]

def _severidade_resultado(resultado):
    if hasattr(resultado, "como_dict"):
        dados = resultado.como_dict()
        return _normalizar(
            dados.get("severidade")
        )

    return _normalizar(
        getattr(
            resultado,
            "severidade",
            "",
        )
    )


def _resultado_relevante(resultado):
    """
    Somente alerta/critico entra automaticamente
    no parecer como achado.

    Resultado informativo nao e tratado como
    irregularidade.
    """

    return _severidade_resultado(
        resultado
    ) in {
        "alerta",
        "warning",
        "critica",
        "cr?tica",
        "critico",
        "cr?tico",
        "critical",
    }


@transaction.atomic
def gerar_itens_iniciais_parecer(
    *,
    parecer,
    usuario,
):
    """
    Executa o PGP Rules sobre a prestacao vinculada
    e cria os itens iniciais do Parecer Tecnico.

    O processo:
    - nao aprova o parecer;
    - nao conclui item automaticamente;
    - nao registra glosa;
    - nao altera lancamento/documento;
    - exige revisao humana posterior.
    """

    if not isinstance(
        parecer,
        ParecerTecnico,
    ):
        raise ValidationError(
            "Parecer invalido para geracao de itens."
        )

    if (
        usuario is None
        or not getattr(usuario, "pk", None)
    ):
        raise ValidationError(
            "A geracao de itens exige usuario responsavel."
        )

    prestacao = parecer.prestacao
    empresa = parecer.empresa
    termo = getattr(
        prestacao,
        "termo",
        None,
    )

    # Evita duplicacao caso o servico seja chamado
    # novamente para o mesmo parecer.
    if parecer.itens.exists():
        return parecer.itens.count()

    lancamentos = (
        Lancamento.objects
        .filter(
            empresa=empresa,
        )
        .filter(
            Q(prestacao=prestacao)
            | (
                Q(termo=termo)
                if termo is not None
                else Q(pk__in=[])
            )
        )
        .distinct()
        .order_by("pk")
    )

    documentos = (
        Documento.objects
        .filter(
            empresa=empresa,
        )
        .filter(
            Q(prestacao=prestacao)
            | Q(lancamento__in=lancamentos)
            | (
                Q(termo=termo)
                if termo is not None
                else Q(pk__in=[])
            )
        )
        .distinct()
        .order_by("pk")
    )

    documentos_avulsos = (
        documentos
        .exclude(
            lancamento__in=lancamentos
        )
        .order_by("pk")
    )

    ordem = 0
    criados = 0
    falhas = []

    # --------------------------------------------------------
    # LANCAMENTOS
    # --------------------------------------------------------

    for lancamento in lancamentos:
        try:
            resultados = (
                motor_regras
                .analisar_lancamento(
                    lancamento
                )
            )
        except Exception as erro:
            falhas.append(
                "Lancamento "
                f"{lancamento.pk}: "
                f"{erro}"
            )
            continue

        for resultado in _resultados_do_motor(
            resultados
        ):

            if not _resultado_relevante(
                resultado
            ):
                continue

            ordem += 1

            incorporar_resultado_regra(
                parecer=parecer,
                resultado=resultado,
                usuario=usuario,
                lancamento=lancamento,
                ordem=ordem,
            )

            criados += 1

    # --------------------------------------------------------
    # DOCUMENTOS
    # --------------------------------------------------------

    for documento in documentos_avulsos:
        try:
            resultados = (
                motor_regras
                .analisar_documento(
                    documento
                )
            )
        except Exception as erro:
            falhas.append(
                "Documento "
                f"{documento.pk}: "
                f"{erro}"
            )
            continue

        for resultado in _resultados_do_motor(
            resultados
        ):

            if not _resultado_relevante(
                resultado
            ):
                continue

            ordem += 1

            incorporar_resultado_regra(
                parecer=parecer,
                resultado=resultado,
                usuario=usuario,
                lancamento=documento.lancamento,
                documento=documento,
                ordem=ordem,
            )

            criados += 1

    # --------------------------------------------------------
    # SE NAO HOUVE ACHADO RELEVANTE
    # --------------------------------------------------------

    if criados == 0:

        ordem += 1

        descricao = (
            "O PGP Rules executou as verificacoes "
            "automaticas disponiveis para os lancamentos "
            "e documentos vinculados a prestacao e nao "
            "identificou achados classificados como "
            "alerta ou critico."
        )

        if falhas:
            descricao += (
                " Houve falha tecnica em "
                f"{len(falhas)} verificacao(oes), "
                "que devem ser conferidas manualmente."
            )

        item = ItemParecer(
            parecer=parecer,
            codigo="CONTROLE-AUTOMATICO",
            codigo_regra="",
            categoria=(
                ItemParecer
                .Categoria
                .DOCUMENTAL
            ),
            severidade=(
                ItemParecer
                .Severidade
                .INFORMATIVA
            ),
            origem=(
                ItemParecer
                .Origem
                .PGP_RULES
            ),
            titulo=(
                "Verificacao automatica "
                "sem achados relevantes"
            ),
            descricao=descricao,
            fato_verificado=(
                "Nenhum achado automatico classificado "
                "como alerta ou critico."
            ),
            recomendacao=(
                "Realizar a conferencia humana integral "
                "antes da conclusao do parecer."
            ),
            resultado_origem=(
                "SEM_ACHADO_RELEVANTE"
            ),
            dados_origem={
                "lancamentos_verificados":
                    lancamentos.count(),
                "documentos_verificados":
                    documentos.count(),
                "falhas_tecnicas":
                    falhas,
            },
            ordem=ordem,
            criado_por=usuario,
            conclusao_item=(
                ItemParecer
                .ConclusaoItem
                .NAO_ANALISADO
            ),
            manifestacao_analista="",
        )

        item.full_clean()
        item.save()

        criados += 1

    return criados
