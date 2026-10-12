import unicodedata
from django.db.models import Count, Q

from apps.assistente_ia.models import ProcessamentoAssistido

from apps.conciliacao.models import Conciliacao
from apps.core.permissoes_modulos import modulo_liberado
from apps.diligencias.models import Diligencia
from apps.documentos.models import Documento
from apps.lancamentos.models import Lancamento
from apps.pareceres.models import ParecerTecnico
from apps.planos_trabalho.models import PlanoTrabalho
from apps.prestacao.models import Prestacao



def _resumo_choices(queryset, campo, limite=4):
    """
    Resume os valores de um campo com choices.
    Ex.: Regular: 31 • Aprovado com ressalva: 1
    """

    if not queryset.exists():
        return "Sem registros"

    field = queryset.model._meta.get_field(campo)

    escolhas = dict(
        getattr(
            field,
            "flatchoices",
            [],
        )
    )

    contagens = (
        queryset
        .values(campo)
        .annotate(total=Count("pk"))
        .order_by("-total", campo)
    )

    partes = []

    for linha in contagens[:limite]:
        valor = linha[campo]
        rotulo = escolhas.get(
            valor,
            valor or "Não informado",
        )

        partes.append(
            f"{rotulo}: {linha['total']}"
        )

    return " • ".join(partes)


def _status_objeto(objeto, campos=("status", "situacao")):
    """
    Obtém de forma segura o status de um objeto individual.
    """

    if objeto is None:
        return "Não vinculado"

    nomes_campos = {
        field.name
        for field in objeto._meta.fields
    }

    for campo in campos:
        if campo not in nomes_campos:
            continue

        metodo = getattr(
            objeto,
            f"get_{campo}_display",
            None,
        )

        if callable(metodo):
            return metodo()

        valor = getattr(
            objeto,
            campo,
            None,
        )

        if valor:
            return str(valor)

    return "Vinculado"


def _classe_status(resumo):
    """
    Define apenas a apresentacao visual do resumo.

    A comparacao ignora acentos para evitar dependencia
    de codificacao na classificacao visual.

    Nao altera situacao, conclusao ou regra de negocio.
    """

    valor_original = str(
        resumo or ""
    ).strip().lower()

    valor = "".join(
        caractere
        for caractere in unicodedata.normalize(
            "NFKD",
            valor_original,
        )
        if not unicodedata.combining(
            caractere
        )
    )

    criticos = (
        "reprov",
        "irregular",
        "glosa",
        "nao atend",
        "com erro",
        "critic",
    )

    alertas = (
        "ressalva",
        "pendencia",
        "em diligencia",
        "em revisao",
        "reanalise",
        "aguardando",
        "inconclusivo",
    )

    positivos = (
        "vigente",
        "aprovad",
        "regular",
        "conferido",
        "fechada",
        "atendida",
        "sugestao aceita",
        "finalizado",
        "sem pendencias relevantes",
        "concluid",
    )

    andamento = (
        "rascunho",
        "em analise",
        "em elaboracao",
        "respondida",
        "enviada",
        "visualizada",
    )

    neutros = (
        "sem registros",
        "nao vinculado",
        "nao informado",
        "encerrado para demonstracao",
    )

    if any(
        termo in valor
        for termo in criticos
    ):
        return "badge-danger"

    if any(
        termo in valor
        for termo in alertas
    ):
        return "badge-warning"

    if any(
        termo in valor
        for termo in positivos
    ):
        return "badge-success"

    if any(
        termo in valor
        for termo in andamento
    ):
        return "badge-info"

    if any(
        termo in valor
        for termo in neutros
    ):
        return "badge-secondary"

    return "badge-light"

def montar_fluxo_parceria(parceria, user):
    """
    Consolida os objetos pertencentes ao mesmo fluxo funcional
    da parceria, respeitando as permissoes de modulo do usuario.

    A cadeia utilizada e:
    Parceria -> Termo -> Plano -> Prestacao -> Lancamento ->
    Documento -> Conciliacao -> Diligencia -> Parecer.
    """

    termo = parceria.numtermo
    empresa = parceria.empresa

    vazio_plano = PlanoTrabalho.objects.none()
    vazio_prestacao = Prestacao.objects.none()
    vazio_lancamento = Lancamento.objects.none()
    vazio_documento = Documento.objects.none()
    vazio_conciliacao = Conciliacao.objects.none()
    vazio_diligencia = Diligencia.objects.none()
    vazio_parecer = ParecerTecnico.objects.none()
    vazio_processamento = ProcessamentoAssistido.objects.none()

    resultado = {
        "termo": None,
        "planos": vazio_plano,
        "prestacoes": vazio_prestacao,
        "lancamentos": vazio_lancamento,
        "documentos": vazio_documento,
        "conciliacoes": vazio_conciliacao,
        "diligencias": vazio_diligencia,
        "pareceres": vazio_parecer,
        "processamentos": vazio_processamento,
        "totais": {
            "planos": 0,
            "prestacoes": 0,
            "lancamentos": 0,
            "documentos": 0,
            "conciliacoes": 0,
            "diligencias": 0,
            "pareceres": 0,
            "processamentos": 0,
        },
    }

    if termo is None or empresa is None:
        return resultado

    # Querysets-base servem apenas para determinar a cadeia.
    # A exposicao ao usuario continua condicionada ao modulo.
    prestacoes_base = Prestacao.objects.filter(
        termo=termo,
        empresa=empresa,
    )

    lancamentos_base = Lancamento.objects.filter(
        termo=termo,
        empresa=empresa,
    )

    documentos_base = (
        Documento.objects
        .filter(empresa=empresa)
        .filter(
            Q(termo=termo)
            | Q(prestacao__in=prestacoes_base)
            | Q(lancamento__in=lancamentos_base)
        )
        .distinct()
    )

    if modulo_liberado(user, "termos"):
        resultado["termo"] = termo

    if modulo_liberado(
        user,
        "planos_trabalho",
    ):
        resultado["planos"] = (
            PlanoTrabalho.objects
            .filter(termo=termo)
            .select_related("termo")
            .order_by("-versao", "-pk")
        )

    if modulo_liberado(user, "prestacoes"):
        resultado["prestacoes"] = (
            prestacoes_base
            .select_related(
                "empresa",
                "termo",
            )
            .order_by("-pk")
        )

    if modulo_liberado(user, "lancamentos"):
        resultado["lancamentos"] = (
            lancamentos_base
            .select_related(
                "empresa",
                "termo",
                "prestacao",
            )
            .order_by(
                "-data_documento",
                "-pk",
            )
        )

    if modulo_liberado(user, "documentos"):
        resultado["documentos"] = (
            documentos_base
            .select_related(
                "empresa",
                "termo",
                "prestacao",
                "lancamento",
            )
            .order_by(
                "-atualizado_em",
                "-pk",
            )
        )

    if modulo_liberado(user, "conciliacao"):
        resultado["conciliacoes"] = (
            Conciliacao.objects
            .filter(
                prestacao__in=prestacoes_base
            )
            .select_related(
                "prestacao",
                "prestacao__empresa",
            )
            .order_by(
                "-atualizado_em",
                "-pk",
            )
        )

    if modulo_liberado(user, "diligencias"):
        resultado["diligencias"] = (
            Diligencia.objects
            .filter(empresa=empresa)
            .filter(
                Q(prestacao__in=prestacoes_base)
                | Q(lancamento__in=lancamentos_base)
                | Q(documento__in=documentos_base)
            )
            .select_related(
                "empresa",
                "prestacao",
                "lancamento",
                "documento",
            )
            .distinct()
            .order_by(
                "-criado_em",
                "-pk",
            )
        )

    if modulo_liberado(user, "assistente_ia"):
        resultado["processamentos"] = (
            ProcessamentoAssistido.objects
            .filter(
                empresa=empresa,
                documento__in=documentos_base,
            )
            .select_related(
                "documento",
                "empresa",
                "solicitado_por",
                "revisado_por",
            )
            .prefetch_related("achados")
            .order_by("-criado_em", "-pk")
        )

    if modulo_liberado(user, "pareceres"):
        resultado["pareceres"] = (
            ParecerTecnico.objects
            .filter(
                empresa=empresa,
                prestacao__in=prestacoes_base,
            )
            .select_related(
                "empresa",
                "prestacao",
            )
            .order_by(
                "-pk",
            )
        )

    for chave in (
        "planos",
        "prestacoes",
        "lancamentos",
        "documentos",
        "conciliacoes",
        "diligencias",
        "pareceres",
        "processamentos",
    ):
        resultado["totais"][chave] = (
            resultado[chave].count()
        )


    resultado["resumos"] = {
        "termo": (
            _status_objeto(
                resultado["termo"]
            )
            if resultado["termo"]
            else "Não vinculado"
        ),
        "planos": _resumo_choices(
            resultado["planos"],
            "situacao",
        ),
        "prestacoes": _resumo_choices(
            resultado["prestacoes"],
            "situacao_workflow",
        ),
        "lancamentos": _resumo_choices(
            resultado["lancamentos"],
            "situacao",
        ),
        "documentos": _resumo_choices(
            resultado["documentos"],
            "status",
        ),
        "conciliacoes": _resumo_choices(
            resultado["conciliacoes"],
            "situacao",
        ),
        "diligencias": _resumo_choices(
            resultado["diligencias"],
            "status",
        ),
        "processamentos": _resumo_choices(
            resultado["processamentos"],
            "decisao_revisor",
        ),
        "pareceres": (
            (
                resultado["pareceres"][0]
                .get_situacao_display()
                + " • "
                + resultado["pareceres"][0]
                .get_tipo_conclusao_display()
            )
            if resultado["pareceres"].exists()
            else "Sem registros"
        ),
    }


    resultado["classes_status"] = {
        chave: _classe_status(valor)
        for chave, valor
        in resultado["resumos"].items()
    }

    return resultado
