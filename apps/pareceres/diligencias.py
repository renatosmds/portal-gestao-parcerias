from django.core.exceptions import ValidationError
from django.db import transaction

from apps.diligencias.models import Diligencia
from apps.pareceres.auditoria import (
    registrar_diligencia_criada,
)
from apps.pareceres.models import ItemParecer


def _limpar(valor):
    return " ".join(
        str(valor or "").split()
    )


def _descricao_diligencia(item):
    partes = []

    if item.fato_verificado:
        partes.append(
            "Fato verificado: "
            + _limpar(item.fato_verificado)
        )

    if item.evidencia:
        partes.append(
            "Evid?ncia: "
            + _limpar(item.evidencia)
        )

    if item.recomendacao:
        partes.append(
            "Provid?ncia sugerida: "
            + _limpar(item.recomendacao)
        )

    if not partes and item.descricao:
        partes.append(
            _limpar(item.descricao)
        )

    if not partes:
        partes.append(
            "Achado pendente de esclarecimento ou documenta??o complementar."
        )

    return "\n\n".join(partes)


@transaction.atomic
def criar_diligencia_do_item(
    *,
    item,
    usuario,
    prazo_resposta=None,
    prioridade=Diligencia.Prioridade.NORMAL,
    responsavel=None,
    assunto=None,
):
    """
    Cria diligencia em RASCUNHO a partir de ItemParecer.

    Esta funcao:
    - preserva segregacao por OSC/prestacao;
    - reutiliza lancamento/documento do item;
    - nao envia automaticamente a diligencia;
    - nao altera conclusao do item;
    - nao altera conclusao do parecer;
    - nao registra glosa;
    - vincula a diligencia criada ao ItemParecer.
    """

    if not isinstance(item, ItemParecer):
        raise ValidationError(
            "O item informado nao e um ItemParecer valido."
        )

    if not item.pk:
        raise ValidationError(
            "O ItemParecer deve estar salvo antes da criacao da diligencia."
        )

    if usuario is None or not getattr(usuario, "pk", None):
        raise ValidationError(
            "A criacao da diligencia exige usuario responsavel."
        )

    if item.diligencia_id:
        raise ValidationError(
            "Este item do parecer ja possui diligencia vinculada."
        )

    parecer = item.parecer

    if (
        not parecer.prestacao_id
        or not parecer.empresa_id
    ):
        raise ValidationError(
            "O parecer deve possuir prestacao e empresa definidas."
        )

    prioridades_validas = {
        valor
        for valor, _rotulo
        in Diligencia.Prioridade.choices
    }

    if prioridade not in prioridades_validas:
        raise ValidationError(
            "Prioridade de diligencia invalida."
        )

    titulo = _limpar(
        assunto
        or item.titulo
        or "Diligencia de prestacao de contas"
    )

    descricao = _descricao_diligencia(item)

    fundamento = _limpar(
        item.fundamentacao
    )

    diligencia = Diligencia(
        assunto=titulo[:180],
        descricao=descricao,
        fundamento=fundamento,
        prioridade=prioridade,
        status=Diligencia.Status.RASCUNHO,
        prazo_resposta=prazo_resposta,
        empresa=parecer.empresa,
        prestacao=parecer.prestacao,
        lancamento=item.lancamento,
        documento=item.documento,
        responsavel=responsavel,
        criada_por=usuario,
    )

    diligencia.full_clean()
    diligencia.save()

    item.diligencia = diligencia

    # A validacao do ItemParecer confirma novamente
    # empresa e prestacao compativeis.
    item.full_clean()
    item.save(
        update_fields=[
            "diligencia",
            "atualizado_em",
        ]
    )

    registrar_diligencia_criada(
        item=item,
        diligencia=diligencia,
        usuario=usuario,
    )

    return diligencia
