from collections import defaultdict
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.financeiro.models import (
    ImportacaoOFX,
    MovimentacaoFinanceira,
)
from apps.financeiro.ofx import parse_ofx


def _data_ofx(valor):
    return datetime.strptime(
        valor[:8],
        "%Y%m%d",
    ).date()


def _mascarar_conta(conta):
    conta = (conta or "").strip()

    if not conta:
        return ""

    if len(conta) <= 4:
        return "*" * len(conta)

    return (
        "*" * (len(conta) - 4)
        + conta[-4:]
    )


def _tipo_movimentacao(movimento):
    memo = (
        movimento.memo
        or ""
    ).strip().upper()

    if memo == "RESG AUT":
        return (
            MovimentacaoFinanceira
            .Tipo
            .RESGATE_AUTOMATICO
        )

    if memo in {
        "ES.ENV.TED",
        "DEV. TED",
    }:
        return (
            MovimentacaoFinanceira
            .Tipo
            .ESTORNO
        )

    if movimento.tipo.upper() == "DEBIT":
        return (
            MovimentacaoFinanceira
            .Tipo
            .DEBITO_AUTORIZADO
        )

    if movimento.tipo.upper() == "CREDIT":
        return (
            MovimentacaoFinanceira
            .Tipo
            .CREDITO_AUTORIZADO
        )

    raise ValidationError(
        {
            "tipo_ofx": (
                "Tipo OFX nao reconhecido: "
                f"{movimento.tipo}"
            )
        }
    )


def _assinatura_base(
    *,
    extrato,
    movimento,
):
    partes = [
        (extrato.banco or "").strip(),
        (extrato.conta or "").strip(),
        movimento.data_postagem.isoformat(),
        str(movimento.valor),
        (movimento.tipo or "").strip().upper(),
        (movimento.fitid or "").strip(),
        (movimento.checknum or "").strip(),
        (movimento.memo or "").strip().upper(),
    ]

    return "\x1f".join(partes)


def _hash_movimento(
    *,
    assinatura_base,
    ocorrencia,
):
    conteudo = (
        f"{assinatura_base}"
        f"\x1f{ocorrencia}"
    )

    return sha256(
        conteudo.encode("utf-8")
    ).hexdigest()


def _eh_estorno_ou_devolucao(movimento):
    memo = (
        movimento.memo_ofx
        or ""
    ).strip().upper()

    return (
        movimento.tipo
        == MovimentacaoFinanceira.Tipo.ESTORNO
        or memo in {
            "ES.ENV.TED",
            "DEV. TED",
        }
    )


def relacionar_estornos(importacao):
    movimentos = list(
        importacao.movimentos
        .order_by(
            "data_hora_ofx",
            "ordem_ofx",
            "id",
        )
    )

    debitos_por_chave = {}

    for movimento in movimentos:

        if (
            movimento.tipo_ofx.upper()
            == "DEBIT"
        ):
            chave = (
                movimento.fitid,
                abs(
                    movimento.valor_ofx
                    or movimento.valor
                ),
            )

            debitos_por_chave.setdefault(
                chave,
                [],
            ).append(
                movimento
            )

            continue

        if not _eh_estorno_ou_devolucao(
            movimento
        ):
            continue

        chave = (
            movimento.fitid,
            abs(
                movimento.valor_ofx
                or movimento.valor
            ),
        )

        candidatos = debitos_por_chave.get(
            chave,
            [],
        )

        if not candidatos:
            continue

        original = candidatos[-1]

        movimento.movimento_relacionado = (
            original
        )

        movimento.save(
            update_fields=[
                "movimento_relacionado",
            ]
        )



@transaction.atomic
def importar_ofx(
    caminho,
    *,
    empresa,
    termo,
    usuario,
    prestacao=None,
    competencia=None,
):
    caminho = Path(caminho)

    dados = caminho.read_bytes()

    hash_arquivo = sha256(
        dados
    ).hexdigest()

    existente = (
        ImportacaoOFX.objects
        .filter(
            empresa=empresa,
            termo=termo,
            hash_arquivo=hash_arquivo,
        )
        .first()
    )

    if existente:
        return existente, False

    extrato = parse_ofx(
        caminho
    )

    importacao = ImportacaoOFX(
        empresa=empresa,
        termo=termo,
        prestacao=prestacao,
        nome_arquivo=caminho.name,
        hash_arquivo=hash_arquivo,
        banco=extrato.banco,
        conta_mascarada=_mascarar_conta(
            extrato.conta
        ),
        tipo_conta=extrato.tipo_conta,
        moeda=extrato.moeda,
        data_inicio=_data_ofx(
            extrato.data_inicio
        ),
        data_fim=_data_ofx(
            extrato.data_fim
        ),
        saldo_informado=extrato.saldo,
        data_saldo=_data_ofx(
            extrato.data_saldo
        ),
        quantidade_movimentos=len(
            extrato.movimentos
        ),
        importado_por=usuario,
    )

    importacao.full_clean()
    importacao.save()

    ocorrencias = defaultdict(int)

    candidatos = []

    for ordem, movimento in enumerate(
        extrato.movimentos,
        start=1,
    ):
        valor_absoluto = abs(
            movimento.valor
        )

        if valor_absoluto == 0:
            raise ValidationError(
                {
                    "valor": (
                        "Movimento OFX com "
                        "valor zero nao pode "
                        "ser importado."
                    )
                }
            )

        tipo = _tipo_movimentacao(
            movimento
        )

        assinatura = _assinatura_base(
            extrato=extrato,
            movimento=movimento,
        )

        ocorrencias[assinatura] += 1

        hash_movimento = _hash_movimento(
            assinatura_base=assinatura,
            ocorrencia=(
                ocorrencias[assinatura]
            ),
        )

        candidatos.append(
            MovimentacaoFinanceira(
                empresa=empresa,
                termo=termo,
                prestacao=prestacao,
                competencia=competencia,
                data=(
                    movimento
                    .data_postagem
                    .date()
                ),
                tipo=tipo,
                valor=valor_absoluto,
                descricao=(
                    movimento.memo
                    or "Movimento OFX"
                )[:255],
                criado_por=usuario,
                importacao_ofx=importacao,
                ordem_ofx=ordem,
                tipo_ofx=(
                    movimento.tipo
                    or ""
                )[:20],
                data_hora_ofx=(
                    movimento
                    .data_postagem
                ),
                valor_ofx=(
                    movimento.valor
                ),
                fitid=(
                    movimento.fitid
                    or ""
                )[:255],
                hash_movimento=hash_movimento,
                checknum=(
                    movimento.checknum
                    or ""
                )[:255],
                memo_ofx=(
                    movimento.memo
                    or ""
                )[:255],
            )
        )

    hashes = {
        movimento.hash_movimento
        for movimento
        in candidatos
    }

    hashes_existentes = set(
        MovimentacaoFinanceira.objects
        .filter(
            empresa=empresa,
            termo=termo,
            hash_movimento__in=hashes,
        )
        .values_list(
            "hash_movimento",
            flat=True,
        )
    )

    movimentos_novos = []

    for registro in candidatos:
        if (
            registro.hash_movimento
            in hashes_existentes
        ):
            continue

        registro.full_clean()

        movimentos_novos.append(
            registro
        )

    MovimentacaoFinanceira.objects.bulk_create(
        movimentos_novos
    )


    relacionar_estornos(
        importacao
    )
    return importacao, True
