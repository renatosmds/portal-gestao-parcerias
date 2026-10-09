from django.db.models import Q

from apps.conciliacao.models import Conciliacao
from apps.core.permissoes_modulos import modulo_liberado
from apps.diligencias.models import Diligencia
from apps.documentos.models import Documento
from apps.lancamentos.models import Lancamento
from apps.pareceres.models import ParecerTecnico
from apps.planos_trabalho.models import PlanoTrabalho
from apps.prestacao.models import Prestacao


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

    resultado = {
        "termo": None,
        "planos": vazio_plano,
        "prestacoes": vazio_prestacao,
        "lancamentos": vazio_lancamento,
        "documentos": vazio_documento,
        "conciliacoes": vazio_conciliacao,
        "diligencias": vazio_diligencia,
        "pareceres": vazio_parecer,
        "totais": {
            "planos": 0,
            "prestacoes": 0,
            "lancamentos": 0,
            "documentos": 0,
            "conciliacoes": 0,
            "diligencias": 0,
            "pareceres": 0,
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
    ):
        resultado["totais"][chave] = (
            resultado[chave].count()
        )

    return resultado
