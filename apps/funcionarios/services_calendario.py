import unicodedata

from django.db.models import Q

from .models import (
    CalendarioLaboral,
    Feriado,
)


def normalizar_localidade(valor):

    valor = (
        valor
        or ""
    ).strip()

    valor = unicodedata.normalize(
        "NFKD",
        valor,
    )

    valor = "".join(
        ch
        for ch in valor
        if not unicodedata.combining(
            ch
        )
    )

    return (
        " ".join(
            valor.upper().split()
        )
    )


def calendario_laboral_vigente(
    funcionario,
    data,
):
    """
    Resolve o calendario de trabalho aplicavel.

    Preferencia:
    1. calendario da lotacao/departamento;
    2. calendario geral da empresa.

    O endereco residencial do trabalhador nao
    e utilizado como regra principal de lotacao.
    """

    if not funcionario.empresa_id:
        return None

    base = (
        CalendarioLaboral.objects
        .select_related(
            "empresa",
            "departamento",
        )
        .filter(
            empresa_id=funcionario.empresa_id,
            ativo=True,
            vigencia_inicio__lte=data,
        )
        .filter(
            Q(vigencia_fim__isnull=True)
            | Q(vigencia_fim__gte=data)
        )
    )

    departamentos_ids = list(
        funcionario.departamentos
        .values_list(
            "pk",
            flat=True,
        )
    )

    if departamentos_ids:

        especifico = (
            base
            .filter(
                departamento_id__in=(
                    departamentos_ids
                )
            )
            .order_by(
                "-prioridade",
                "-vigencia_inicio",
                "-pk",
            )
            .first()
        )

        if especifico:
            return especifico

    return (
        base
        .filter(
            departamento__isnull=True,
        )
        .order_by(
            "-prioridade",
            "-vigencia_inicio",
            "-pk",
        )
        .first()
    )


def _feriados_localidade(
    data,
    uf="",
    municipio="",
):

    uf_norm = normalizar_localidade(
        uf
    )

    municipio_norm = normalizar_localidade(
        municipio
    )

    candidatos = list(
        Feriado.objects
        .filter(
            data=data,
            ativo=True,
        )
        .order_by(
            "pk"
        )
    )

    resultado = []

    for feriado in candidatos:

        if (
            feriado.abrangencia
            == "nacional"
        ):
            resultado.append(
                feriado
            )
            continue

        if (
            feriado.abrangencia
            == "estadual"
            and uf_norm
            and normalizar_localidade(
                feriado.uf
            ) == uf_norm
        ):
            resultado.append(
                feriado
            )
            continue

        if (
            feriado.abrangencia
            == "municipal"
            and uf_norm
            and municipio_norm
            and normalizar_localidade(
                feriado.uf
            ) == uf_norm
            and normalizar_localidade(
                feriado.municipio
            ) == municipio_norm
        ):
            resultado.append(
                feriado
            )

    return resultado


def evento_calendario_aplicavel_data(
    funcionario,
    data,
):
    """
    Retorna evento aplicavel ao trabalhador.

    Feriado legal tem prioridade sobre
    ponto facultativo.

    Ponto facultativo somente vira evento
    operacional quando o calendario laboral
    expressamente autoriza.
    """

    calendario = (
        calendario_laboral_vigente(
            funcionario,
            data,
        )
    )

    if calendario:

        uf = calendario.uf
        municipio = calendario.municipio

    else:

        # Fallback apenas para permitir
        # feriados estaduais/municipais quando
        # ainda nao existe calendario formal.
        # O ideal operacional e cadastrar
        # CalendarioLaboral.
        uf = getattr(
            funcionario,
            "estado",
            "",
        )

        municipio = getattr(
            funcionario,
            "cidade",
            "",
        )

    eventos = (
        _feriados_localidade(
            data,
            uf=uf,
            municipio=municipio,
        )
    )

    feriados = [
        item
        for item in eventos
        if item.natureza == "feriado"
    ]

    if feriados:

        prioridade = {
            "municipal": 3,
            "estadual": 2,
            "nacional": 1,
        }

        feriados.sort(
            key=lambda item: (
                prioridade.get(
                    item.abrangencia,
                    0,
                ),
                item.pk,
            ),
            reverse=True,
        )

        return {
            "tipo": "feriado",
            "feriado": feriados[0],
            "calendario": calendario,
        }

    pontos = [
        item
        for item in eventos
        if (
            item.natureza
            == "ponto_facultativo"
        )
    ]

    if (
        pontos
        and calendario
        and calendario
        .considera_ponto_facultativo
    ):

        return {
            "tipo": "ponto_facultativo",
            "feriado": pontos[0],
            "calendario": calendario,
        }

    return None
