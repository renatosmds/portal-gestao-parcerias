from __future__ import annotations

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify


def get_empresa_do_usuario(user):
    """
    Retorna a empresa associada ao funcionário autenticado.

    Em vez de deixar o sistema falhar com AttributeError/RelatedObjectDoesNotExist,
    apresenta uma negação de acesso controlada quando o usuário não possui
    funcionário ou empresa vinculada.
    """
    if not user or not user.is_authenticated:
        raise PermissionDenied("É necessário estar autenticado.")

    try:
        funcionario = user.funcionario
    except Exception as exc:
        raise PermissionDenied(
            "O usuário autenticado não possui funcionário vinculado."
        ) from exc

    if not funcionario.empresa_id:
        raise PermissionDenied(
            "O funcionário autenticado não possui empresa vinculada."
        )

    return funcionario.empresa


def gerar_username_unico(nome_base: str) -> str:
    """
    Gera um username válido e único a partir do campo 'usuario'.

    Exemplos:
        Maria Silva -> maria
        Maria Souza, quando 'maria' já existe -> maria2
    """
    primeiro_nome = (nome_base or "").strip().split(" ")[0]
    base = slugify(primeiro_nome) or "usuario"
    base = base[:140]

    username = base
    contador = 2

    while User.objects.filter(username=username).exists():
        sufixo = str(contador)
        username = f"{base[:150 - len(sufixo)]}{sufixo}"
        contador += 1

    return username


def criar_usuario_para_funcionario(nome_base: str) -> User:
    username = gerar_username_unico(nome_base)
    user = User(username=username)
    user.set_unusable_password()
    user.save()
    return user


# ============================================================
# ETAPA 8.3D - MOTOR DE ESCALAS E JORNADA
# ============================================================

from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models import Q


ZERO_HORAS = Decimal("0.00")


def escala_funcionario_vigente(
    funcionario,
    data,
):
    """
    Retorna o vinculo de escala vigente para o colaborador
    na data informada.

    Historico:
    nao usa o campo 'ativo' da escala para apagar o passado.
    A vigencia e determinada pelas datas.
    """
    from .models import EscalaFuncionario

    return (
        EscalaFuncionario.objects
        .select_related("escala")
        .filter(
            funcionario=funcionario,
            data_inicio__lte=data,
        )
        .filter(
            Q(data_fim__isnull=True)
            | Q(data_fim__gte=data)
        )
        .order_by(
            "-data_inicio",
            "-pk",
        )
        .first()
    )


def posicao_ciclo_escala(
    escala_funcionario,
    data,
):
    """
    Calcula a posicao da data dentro do ciclo.

    Exemplos:
    - ciclo de 7 dias -> posicoes 1 a 7
    - ciclo 12x36 -> posicoes 1 e 2

    data_referencia representa a posicao 1.
    """
    ciclo = (
        escala_funcionario.escala.ciclo_dias
    )

    if not ciclo or ciclo < 1:
        raise ValidationError(
            "A escala possui ciclo invalido."
        )

    diferenca = (
        data
        - escala_funcionario.data_referencia
    ).days

    return (
        diferenca % ciclo
    ) + 1


def funcionario_em_periodo_contratual(
    funcionario,
    data,
):
    """
    Verifica se a data esta dentro do periodo contratual.
    """
    if (
        funcionario.data_admissao
        and data < funcionario.data_admissao
    ):
        return False

    if (
        funcionario.data_desligamento
        and data > funcionario.data_desligamento
    ):
        return False

    return True


def apurar_jornada_prevista_data(
    funcionario,
    data,
):
    """
    Apura a jornada prevista de um colaborador em uma data.

    Nao inventa jornada.

    Retorno:
    {
        "data": ...,
        "em_periodo_contratual": bool,
        "tem_escala": bool,
        "configurada": bool,
        "escala_funcionario": obj/None,
        "escala": obj/None,
        "posicao_ciclo": int/None,
        "jornada": obj/None,
        "trabalha": bool,
        "horas_previstas": Decimal,
        "motivo": str,
    }
    """
    from .models import JornadaEscala

    resultado = {
        "data": data,
        "em_periodo_contratual": False,
        "tem_escala": False,
        "configurada": False,
        "escala_funcionario": None,
        "escala": None,
        "posicao_ciclo": None,
        "jornada": None,
        "trabalha": False,
        "horas_previstas": ZERO_HORAS,
        "motivo": "",
    }

    if not funcionario_em_periodo_contratual(
        funcionario,
        data,
    ):
        resultado[
            "motivo"
        ] = "fora_periodo_contratual"

        return resultado

    resultado[
        "em_periodo_contratual"
    ] = True

    vinculo = escala_funcionario_vigente(
        funcionario,
        data,
    )

    if not vinculo:
        resultado[
            "motivo"
        ] = "escala_nao_configurada"

        return resultado

    resultado[
        "tem_escala"
    ] = True

    resultado[
        "escala_funcionario"
    ] = vinculo

    resultado[
        "escala"
    ] = vinculo.escala

    posicao = posicao_ciclo_escala(
        vinculo,
        data,
    )

    resultado[
        "posicao_ciclo"
    ] = posicao

    jornada = (
        JornadaEscala.objects
        .filter(
            escala=vinculo.escala,
            posicao_ciclo=posicao,
        )
        .first()
    )

    if not jornada:
        resultado[
            "motivo"
        ] = "posicao_ciclo_nao_configurada"

        return resultado

    resultado[
        "configurada"
    ] = True

    resultado[
        "jornada"
    ] = jornada

    resultado[
        "trabalha"
    ] = jornada.trabalha

    if jornada.trabalha:
        resultado[
            "horas_previstas"
        ] = (
            jornada.horas_previstas
            or ZERO_HORAS
        )
    else:
        resultado[
            "horas_previstas"
        ] = ZERO_HORAS

    resultado[
        "motivo"
    ] = (
        "trabalho"
        if jornada.trabalha
        else "descanso"
    )

    return resultado


def horas_previstas_periodo(
    funcionario,
    data_inicio,
    data_fim,
    exigir_configuracao=True,
):
    """
    Soma as horas previstas entre duas datas.

    Se houver dia dentro do periodo contratual sem escala
    ou sem posicao de ciclo configurada, interrompe o
    calculo por padrao.

    Isso evita que a folha seja calculada com zero horas
    por falta de cadastro.
    """
    if data_fim < data_inicio:
        raise ValidationError(
            "A data final nao pode ser anterior "
            "a data inicial."
        )

    total = ZERO_HORAS
    dias_trabalho = 0
    dias_descanso = 0
    dias_sem_configuracao = []
    detalhe = []

    atual = data_inicio

    while atual <= data_fim:

        apuracao = (
            apurar_jornada_prevista_data(
                funcionario,
                atual,
            )
        )

        detalhe.append(
            apuracao
        )

        if (
            apuracao[
                "em_periodo_contratual"
            ]
            and not apuracao[
                "configurada"
            ]
        ):
            dias_sem_configuracao.append(
                atual
            )

        if apuracao["configurada"]:

            if apuracao["trabalha"]:
                dias_trabalho += 1

                total += apuracao[
                    "horas_previstas"
                ]

            else:
                dias_descanso += 1

        atual += timedelta(
            days=1
        )

    if (
        exigir_configuracao
        and dias_sem_configuracao
    ):
        datas = ", ".join(
            data.strftime(
                "%d/%m/%Y"
            )
            for data
            in dias_sem_configuracao[:5]
        )

        complemento = (
            "..."
            if len(
                dias_sem_configuracao
            ) > 5
            else ""
        )

        raise ValidationError(
            "Existem dias do periodo contratual "
            "sem escala/jornada configurada: "
            f"{datas}{complemento}"
        )

    return {
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "horas_previstas": (
            total.quantize(
                Decimal("0.01")
            )
        ),
        "dias_trabalho": dias_trabalho,
        "dias_descanso": dias_descanso,
        "dias_sem_configuracao": (
            dias_sem_configuracao
        ),
        "detalhe": detalhe,
    }


def limites_competencia(
    competencia,
):
    """
    Retorna primeiro e ultimo dia do mes.
    """
    from calendar import monthrange
    from datetime import date

    primeiro = date(
        competencia.year,
        competencia.month,
        1,
    )

    ultimo = date(
        competencia.year,
        competencia.month,
        monthrange(
            competencia.year,
            competencia.month,
        )[1],
    )

    return primeiro, ultimo


def horas_previstas_competencia_escala(
    funcionario,
    competencia,
    exigir_configuracao=True,
):
    """
    Calcula a jornada prevista de uma competencia
    utilizando o historico de escalas.

    Suporta mudanca de escala dentro do proprio mes.
    """
    inicio, fim = limites_competencia(
        competencia
    )

    return horas_previstas_periodo(
        funcionario=funcionario,
        data_inicio=inicio,
        data_fim=fim,
        exigir_configuracao=(
            exigir_configuracao
        ),
    )


# ============================================================
# ETAPA 8.3E - VALIDACOES TRABALHISTAS
# ============================================================


def _minutos_horario(
    valor,
):
    return (
        valor.hour * 60
        + valor.minute
    )


def _duracao_entre_horarios(
    inicio,
    fim,
):
    """
    Calcula minutos entre dois horarios.

    Se a saida for menor ou igual a entrada,
    considera encerramento no dia seguinte.
    """
    minutos_inicio = (
        _minutos_horario(
            inicio
        )
    )

    minutos_fim = (
        _minutos_horario(
            fim
        )
    )

    if minutos_fim <= minutos_inicio:
        minutos_fim += 24 * 60

    return (
        minutos_fim
        - minutos_inicio
    )


def _horas_liquidas_jornada(
    jornada,
):
    """
    Calcula horas liquidas apenas quando entrada e
    saida estiverem informadas.

    O intervalo cadastrado e descontado.
    """
    if (
        not jornada.hora_entrada
        or not jornada.hora_saida
    ):
        return None

    minutos = _duracao_entre_horarios(
        jornada.hora_entrada,
        jornada.hora_saida,
    )

    minutos -= (
        jornada.intervalo_minutos
        or 0
    )

    if minutos < 0:
        return None

    return (
        Decimal(minutos)
        / Decimal("60")
    ).quantize(
        Decimal("0.01")
    )


def _intervalo_minimo_referencia(
    horas_previstas,
):
    """
    Referencia geral do art. 71 da CLT.

    Ate 4h:
        sem minimo geral nesta funcao.

    Acima de 4h ate 6h:
        15 minutos.

    Acima de 6h:
        60 minutos como regra geral.

    ACT/CCT ou regra especial pode exigir tratamento
    diferente e deve ser registrado no fundamento.
    """
    if horas_previstas > Decimal("6.00"):
        return 60

    if horas_previstas > Decimal("4.00"):
        return 15

    return 0


def validar_escala_trabalhista(
    escala,
):
    """
    Analisa uma escala cadastrada.

    Retorna:
    {
        "valida": bool,
        "erros": [],
        "alertas": [],
        "informacoes": [],
    }

    Erro:
        inconsistencia objetiva de cadastro.

    Alerta:
        situacao que precisa de fundamento ou
        conferencia juridica/coletiva.

    O validador nao substitui ACT, CCT, categoria
    profissional ou normas especiais.
    """
    jornadas = list(
        escala.jornadas_ciclo
        .all()
        .order_by(
            "posicao_ciclo"
        )
    )

    erros = []
    alertas = []
    informacoes = []

    posicoes = {
        jornada.posicao_ciclo
        for jornada
        in jornadas
    }

    esperadas = set(
        range(
            1,
            escala.ciclo_dias + 1,
        )
    )

    faltantes = sorted(
        esperadas
        - posicoes
    )

    excedentes = sorted(
        posicoes
        - esperadas
    )

    if faltantes:
        erros.append(
            "Ciclo incompleto. "
            "Posicoes sem configuracao: "
            + ", ".join(
                str(x)
                for x in faltantes
            )
            + "."
        )

    if excedentes:
        erros.append(
            "Existem posicoes fora do ciclo: "
            + ", ".join(
                str(x)
                for x in excedentes
            )
            + "."
        )

    trabalho = [
        jornada
        for jornada
        in jornadas
        if jornada.trabalha
    ]

    descanso = [
        jornada
        for jornada
        in jornadas
        if not jornada.trabalha
    ]

    if not trabalho:
        erros.append(
            "A escala nao possui nenhum dia "
            "de trabalho."
        )

    if not descanso:
        alertas.append(
            "A escala nao possui dia de descanso "
            "no ciclo cadastrado. Conferir repouso "
            "semanal e regime especial aplicavel."
        )

    if escala.tipo == "5x2":
        if (
            escala.ciclo_dias != 7
            or len(trabalho) != 5
            or len(descanso) != 2
        ):
            erros.append(
                "Escala 5x2 deve possuir ciclo de "
                "7 dias, com 5 dias de trabalho e "
                "2 dias de descanso."
            )

    if escala.tipo == "6x1":
        if (
            escala.ciclo_dias != 7
            or len(trabalho) != 6
            or len(descanso) != 1
        ):
            erros.append(
                "Escala 6x1 deve possuir ciclo de "
                "7 dias, com 6 dias de trabalho e "
                "1 dia de descanso."
            )

    if escala.tipo == "12x36":
        if (
            escala.ciclo_dias != 2
            or len(trabalho) != 1
            or len(descanso) != 1
        ):
            erros.append(
                "Escala 12x36 deve possuir ciclo "
                "alternado de 2 dias: trabalho e "
                "descanso."
            )
        elif (
            trabalho[0].horas_previstas
            != Decimal("12.00")
        ):
            erros.append(
                "Na escala 12x36 o dia de trabalho "
                "deve possuir 12 horas previstas."
            )

    soma_horas = sum(
        (
            jornada.horas_previstas
            or ZERO_HORAS
        )
        for jornada in trabalho
    )

    if escala.ciclo_dias == 7:
        informacoes.append(
            "Carga prevista no ciclo semanal: "
            f"{soma_horas} horas."
        )

        if (
            escala.jornada_semanal_referencia
            is not None
            and soma_horas
            != escala.jornada_semanal_referencia
        ):
            erros.append(
                "A soma das horas do ciclo "
                f"({soma_horas}) difere da jornada "
                "semanal de referencia "
                f"({escala.jornada_semanal_referencia})."
            )

    for jornada in jornadas:

        horas = (
            jornada.horas_previstas
            or ZERO_HORAS
        )

        if (
            not jornada.trabalha
            and horas != ZERO_HORAS
        ):
            erros.append(
                "Posicao "
                f"{jornada.posicao_ciclo}: "
                "dia de descanso possui horas "
                "previstas."
            )

        if not jornada.trabalha:
            continue

        if (
            escala.tipo != "12x36"
            and horas > Decimal("10.00")
        ):
            alertas.append(
                "Posicao "
                f"{jornada.posicao_ciclo}: "
                f"{horas} horas previstas. "
                "A configuracao ultrapassa a "
                "referencia geral de 10 horas "
                "diarias e exige fundamento "
                "especifico."
            )

        elif (
            escala.tipo != "12x36"
            and horas > Decimal("8.00")
        ):
            alertas.append(
                "Posicao "
                f"{jornada.posicao_ciclo}: "
                f"{horas} horas previstas. "
                "A jornada supera 8 horas; "
                "conferir regime de compensacao, "
                "prorrogacao ou instrumento "
                "aplicavel."
            )

        minimo_intervalo = (
            _intervalo_minimo_referencia(
                horas
            )
        )

        if (
            jornada.intervalo_minutos
            < minimo_intervalo
        ):
            alertas.append(
                "Posicao "
                f"{jornada.posicao_ciclo}: "
                "intervalo cadastrado de "
                f"{jornada.intervalo_minutos} min; "
                "referencia geral para esta "
                "duracao: "
                f"{minimo_intervalo} min. "
                "Conferir ACT/CCT ou regra "
                "especial."
            )

        horas_horario = (
            _horas_liquidas_jornada(
                jornada
            )
        )

        if (
            horas_horario is not None
            and abs(
                horas_horario
                - horas
            )
            > Decimal("0.02")
        ):
            erros.append(
                "Posicao "
                f"{jornada.posicao_ciclo}: "
                "horario informado resulta em "
                f"{horas_horario} horas liquidas, "
                "mas horas_previstas esta em "
                f"{horas}."
            )

    # --------------------------------------------------------
    # Interjornada
    # --------------------------------------------------------
    #
    # Analisa pares consecutivos do ciclo, inclusive
    # o retorno da ultima posicao para a primeira.
    #
    # Somente valida quando:
    # - os dois dias sao de trabalho;
    # - saida do primeiro esta informada;
    # - entrada do segundo esta informada.
    #
    # Dias de descanso naturalmente ampliam esse periodo.
    # --------------------------------------------------------

    if jornadas and not faltantes:

        por_posicao = {
            jornada.posicao_ciclo: jornada
            for jornada in jornadas
        }

        for posicao in range(
            1,
            escala.ciclo_dias + 1,
        ):

            atual = por_posicao.get(
                posicao
            )

            proxima_posicao = (
                1
                if posicao
                == escala.ciclo_dias
                else posicao + 1
            )

            proxima = por_posicao.get(
                proxima_posicao
            )

            if (
                not atual
                or not proxima
                or not atual.trabalha
                or not proxima.trabalha
                or not atual.hora_saida
                or not proxima.hora_entrada
            ):
                continue

            saida = (
                _minutos_horario(
                    atual.hora_saida
                )
            )

            entrada = (
                _minutos_horario(
                    proxima.hora_entrada
                )
                + 24 * 60
            )

            descanso_minutos = (
                entrada - saida
            )

            # Se o turno atual cruza meia-noite,
            # sua hora de saida pertence ao dia seguinte.
            if (
                atual.hora_entrada
                and atual.hora_saida
                <= atual.hora_entrada
            ):
                descanso_minutos -= (
                    24 * 60
                )

            if descanso_minutos < 0:
                descanso_minutos += (
                    24 * 60
                )

            if descanso_minutos < 11 * 60:
                erros.append(
                    "Entre as posicoes "
                    f"{posicao} e {proxima_posicao}, "
                    "o descanso calculado e de "
                    f"{descanso_minutos} minutos, "
                    "inferior a 11 horas."
                )

    return {
        "valida": not erros,
        "erros": erros,
        "alertas": alertas,
        "informacoes": informacoes,
    }


# ============================================================
# ETAPA 8.4C - CALENDARIO DIARIO DA FOLHA DE PONTO
# ============================================================


def ferias_vigente_data(
    funcionario,
    data,
):
    """
    Retorna ferias confirmadas/gozadas vigentes na data.

    Ferias apenas programadas ainda nao alteram
    automaticamente a folha de ponto.
    """
    from .models import FeriasFuncionario

    return (
        FeriasFuncionario.objects
        .filter(
            funcionario=funcionario,
            data_inicio__lte=data,
            data_fim__gte=data,
            status__in=[
                "confirmada",
                "gozada",
            ],
        )
        .order_by(
            "-data_inicio",
            "-pk",
        )
        .first()
    )


def afastamento_vigente_data(
    funcionario,
    data,
):
    """
    Retorna afastamento confirmado vigente na data.
    """
    from .models import AfastamentoFuncionario

    return (
        AfastamentoFuncionario.objects
        .select_related("tipo")
        .filter(
            funcionario=funcionario,
            data_inicio__lte=data,
            data_fim__gte=data,
            status="confirmado",
        )
        .order_by(
            "-data_inicio",
            "-pk",
        )
        .first()
    )


def classificar_dia_folha_ponto(
    funcionario,
    data,
):
    """
    Classifica um dia da folha de ponto.

    Prioridade:
    1. fora do vinculo;
    2. ferias;
    3. afastamento/licenca;
    4. feriado/ponto facultativo aplicavel;
    5. descanso;
    6. trabalho;
    7. falta de configuracao.

    Ferias ou afastamento nao sao transformados
    automaticamente em falta.
    """

    jornada = apurar_jornada_prevista_data(
        funcionario,
        data,
    )

    if not jornada[
        "em_periodo_contratual"
    ]:
        return {
            "tipo_dia": "fora_vinculo",
            "horas_previstas": ZERO_HORAS,
            "horas_abonadas": ZERO_HORAS,
            "escala": None,
            "jornada_escala": None,
            "ferias": None,
            "afastamento": None,
        }

    horas_previstas = (
        jornada["horas_previstas"]
        if jornada["configurada"]
        else ZERO_HORAS
    )

    ferias = ferias_vigente_data(
        funcionario,
        data,
    )

    if ferias:
        return {
            "tipo_dia": "ferias",
            "horas_previstas": horas_previstas,
            "horas_abonadas": horas_previstas,
            "escala": jornada["escala"],
            "jornada_escala": jornada["jornada"],
            "ferias": ferias,
            "afastamento": None,
        }

    afastamento = afastamento_vigente_data(
        funcionario,
        data,
    )

    if afastamento:

        abonadas = (
            horas_previstas
            if afastamento.tipo.abona_ponto
            else ZERO_HORAS
        )

        tipo_dia = (
            "afastamento_abonado"
            if afastamento.tipo.abona_ponto
            else "afastamento_nao_abonado"
        )

        return {
            "tipo_dia": tipo_dia,
            "horas_previstas": horas_previstas,
            "horas_abonadas": abonadas,
            "escala": jornada["escala"],
            "jornada_escala": jornada["jornada"],
            "ferias": None,
            "afastamento": afastamento,
        }


    from .services_calendario import (
        evento_calendario_aplicavel_data,
    )

    evento_calendario = (
        evento_calendario_aplicavel_data(
            funcionario,
            data,
        )
    )

    if evento_calendario:

        return {
            "tipo_dia": (
                evento_calendario[
                    "tipo"
                ]
            ),
            "horas_previstas": (
                horas_previstas
            ),
            "horas_abonadas": (
                horas_previstas
            ),
            "escala": jornada["escala"],
            "jornada_escala": (
                jornada["jornada"]
            ),
            "ferias": None,
            "afastamento": None,
            "feriado": (
                evento_calendario[
                    "feriado"
                ]
            ),
        }

    if not jornada["configurada"]:
        return {
            "tipo_dia": "sem_configuracao",
            "horas_previstas": ZERO_HORAS,
            "horas_abonadas": ZERO_HORAS,
            "escala": jornada["escala"],
            "jornada_escala": None,
            "ferias": None,
            "afastamento": None,
        }

    if not jornada["trabalha"]:
        return {
            "tipo_dia": "descanso",
            "horas_previstas": ZERO_HORAS,
            "horas_abonadas": ZERO_HORAS,
            "escala": jornada["escala"],
            "jornada_escala": jornada["jornada"],
            "ferias": None,
            "afastamento": None,
        }

    return {
        "tipo_dia": "trabalho",
        "horas_previstas": horas_previstas,
        "horas_abonadas": ZERO_HORAS,
        "escala": jornada["escala"],
        "jornada_escala": jornada["jornada"],
        "ferias": None,
        "afastamento": None,
    }


def gerar_calendario_folha_ponto(
    folha_ponto,
):
    """
    Gera ou atualiza a classificacao diaria da competencia.

    Nao apaga marcacoes manuais existentes.

    Campos efetivamente trabalhados, extras e faltas
    nao sao recalculados nesta etapa.
    """
    from datetime import timedelta

    from .models import DiaFolhaPonto

    if folha_ponto.status != "aberta":
        raise ValidationError(
            "Somente folhas de ponto abertas podem "
            "ter o calendario regenerado."
        )

    inicio, fim = limites_competencia(
        folha_ponto.competencia
    )

    atual = inicio
    criados = 0
    atualizados = 0

    while atual <= fim:

        classificacao = (
            classificar_dia_folha_ponto(
                folha_ponto.funcionario,
                atual,
            )
        )

        dia, criado = (
            DiaFolhaPonto.objects.get_or_create(
                folha_ponto=folha_ponto,
                data=atual,
                defaults={
                    "funcionario": (
                        folha_ponto.funcionario
                    ),
                    "tipo_dia": (
                        classificacao[
                            "tipo_dia"
                        ]
                    ),
                    "escala": (
                        classificacao[
                            "escala"
                        ]
                    ),
                    "jornada_escala": (
                        classificacao[
                            "jornada_escala"
                        ]
                    ),
                    "ferias": (
                        classificacao[
                            "ferias"
                        ]
                    ),
                    "afastamento": (
                        classificacao[
                            "afastamento"
                        ]
                    ),
                    "feriado": classificacao.get(
                        "feriado"
                    ),
                    "horas_previstas": (
                        classificacao[
                            "horas_previstas"
                        ]
                    ),
                    "horas_abonadas": (
                        classificacao[
                            "horas_abonadas"
                        ]
                    ),
                },
            )
        )

        if criado:
            criados += 1

        else:
            dia.funcionario = (
                folha_ponto.funcionario
            )

            dia.tipo_dia = (
                classificacao[
                    "tipo_dia"
                ]
            )

            dia.escala = (
                classificacao[
                    "escala"
                ]
            )

            dia.jornada_escala = (
                classificacao[
                    "jornada_escala"
                ]
            )

            dia.ferias = (
                classificacao[
                    "ferias"
                ]
            )

            dia.afastamento = (
                classificacao[
                    "afastamento"
                ]
            )

            dia.feriado = (
                classificacao.get(
                    "feriado"
                )
            )

            dia.horas_previstas = (
                classificacao[
                    "horas_previstas"
                ]
            )

            dia.horas_abonadas = (
                classificacao[
                    "horas_abonadas"
                ]
            )

            dia.full_clean()

            dia.save(
                update_fields=[
                    "funcionario",
                    "tipo_dia",
                    "escala",
                    "jornada_escala",
                    "ferias",
                    "afastamento",
                    "feriado",
                    "horas_previstas",
                    "horas_abonadas",
                    "atualizado_em",
                ]
            )

            atualizados += 1

        atual += timedelta(
            days=1
        )

    return {
        "criados": criados,
        "atualizados": atualizados,
        "total": folha_ponto.dias.count(),
    }


# ============================================================
# ETAPA 8.4D - APURACAO DIARIA EFETIVA
# ============================================================


def _minutos_para_horas(
    minutos,
):
    """
    Converte minutos em horas decimais apenas para
    persistencia/apresentacao.

    O calculo intermediario permanece em minutos.
    """
    return (
        Decimal(minutos)
        / Decimal("60")
    ).quantize(
        Decimal("0.01")
    )


def _marcacoes_informadas(
    dia,
):
    return [
        dia.entrada_1,
        dia.saida_1,
        dia.entrada_2,
        dia.saida_2,
    ]


def _tem_alguma_marcacao(
    dia,
):
    return any(
        valor is not None
        for valor
        in _marcacoes_informadas(
            dia
        )
    )


def _minutos_marcacoes_dia(
    dia,
):
    """
    Calcula o tempo efetivamente trabalhado.

    Formatos aceitos:
    - nenhuma marcacao;
    - entrada_1 + saida_1;
    - entrada_1 + saida_1 + entrada_2 + saida_2.

    Marcacao incompleta nao e presumida.
    """
    marcacoes = _marcacoes_informadas(
        dia
    )

    if not any(
        valor is not None
        for valor in marcacoes
    ):
        return None

    primeiro_completo = (
        dia.entrada_1 is not None
        and dia.saida_1 is not None
    )

    segundo_vazio = (
        dia.entrada_2 is None
        and dia.saida_2 is None
    )

    segundo_completo = (
        dia.entrada_2 is not None
        and dia.saida_2 is not None
    )

    if not primeiro_completo:
        raise ValidationError(
            "Primeiro periodo de ponto incompleto. "
            "Informe entrada_1 e saida_1."
        )

    if not (
        segundo_vazio
        or segundo_completo
    ):
        raise ValidationError(
            "Segundo periodo de ponto incompleto. "
            "Informe entrada_2 e saida_2."
        )

    minutos = _duracao_entre_horarios(
        dia.entrada_1,
        dia.saida_1,
    )

    if segundo_completo:
        minutos += (
            _duracao_entre_horarios(
                dia.entrada_2,
                dia.saida_2,
            )
        )

    return minutos


def apurar_dia_folha_ponto(
    dia,
    salvar=True,
):
    """
    Apura um dia da folha de ponto.

    Regras desta etapa:
    - ferias nao geram falta;
    - afastamentos nao viram falta injustificada;
    - fora do vinculo nao gera saldo;
    - descanso trabalhado vira saldo positivo candidato;
    - dia normal compara horas efetivas com previstas;
    - ausencia total de marcacao permanece pendente;
    - marcacao incompleta gera erro;
    - saldo candidato ainda NAO movimenta banco de horas.
    """

    if dia.folha_ponto.status != "aberta":
        raise ValidationError(
            "Somente folha de ponto aberta pode "
            "ser apurada."
        )

    minutos = _minutos_marcacoes_dia(
        dia
    )

    zero = ZERO_HORAS

    resultado = {
        "status": "",
        "horas_trabalhadas": zero,
        "horas_extras": zero,
        "horas_feriado": zero,
        "horas_abonadas": (
            dia.horas_abonadas
            or zero
        ),
        "horas_compensacao_autorizada": zero,
        "horas_faltas_atrasos": zero,
        "saldo_banco_candidato": zero,
        "mensagem": "",
    }

    # --------------------------------------------------------
    # Fora do vinculo
    # --------------------------------------------------------

    if dia.tipo_dia == "fora_vinculo":

        if minutos is not None:
            raise ValidationError(
                "Existem marcacoes em dia fora do "
                "periodo contratual."
            )

        resultado[
            "status"
        ] = "fora_vinculo"

        resultado[
            "mensagem"
        ] = "Dia fora do periodo contratual."

    # --------------------------------------------------------
    # Ferias
    # --------------------------------------------------------

    elif dia.tipo_dia == "ferias":

        if minutos is not None:
            raise ValidationError(
                "Existem marcacoes durante periodo "
                "classificado como ferias. "
                "Necessaria conferencia."
            )

        resultado[
            "status"
        ] = "ferias"

        resultado[
            "mensagem"
        ] = (
            "Ferias: ausencia de ponto nao e falta."
        )

    # --------------------------------------------------------
    # Afastamentos
    # --------------------------------------------------------

    elif dia.tipo_dia in {
        "afastamento_abonado",
        "afastamento_nao_abonado",
    }:

        if minutos is not None:
            raise ValidationError(
                "Existem marcacoes durante afastamento "
                "ou licenca. Necessaria conferencia."
            )

        resultado[
            "status"
        ] = dia.tipo_dia

        resultado[
            "mensagem"
        ] = (
            "Afastamento/licenca identificado. "
            "Nao classificado como falta injustificada."
        )

    # --------------------------------------------------------
    # Feriado / ponto facultativo
    # --------------------------------------------------------

    elif dia.tipo_dia in {
        "feriado",
        "ponto_facultativo",
    }:

        if minutos is None:

            resultado[
                "status"
            ] = dia.tipo_dia

            resultado[
                "mensagem"
            ] = (
                "Dia especial do calendario laboral "
                "sem marcacoes."
            )

        else:

            horas_efetivas = (
                _minutos_para_horas(
                    minutos
                )
            )

            resultado[
                "horas_trabalhadas"
            ] = horas_efetivas

            if dia.tipo_dia == "feriado":

                resultado[
                    "horas_feriado"
                ] = horas_efetivas

                resultado[
                    "status"
                ] = "feriado_trabalhado"

                resultado[
                    "mensagem"
                ] = (
                    "Trabalho em feriado identificado. "
                    "A remuneracao, compensacao ou banco "
                    "sera definida pelo motor de regras "
                    "aplicavel."
                )

            else:

                resultado[
                    "status"
                ] = (
                    "ponto_facultativo_trabalhado"
                )

                resultado[
                    "mensagem"
                ] = (
                    "Trabalho em ponto facultativo "
                    "identificado. Nenhum adicional "
                    "foi presumido automaticamente."
                )

    # --------------------------------------------------------
    # Sem configuracao
    # --------------------------------------------------------

    elif dia.tipo_dia == "sem_configuracao":

        raise ValidationError(
            "Nao e possivel apurar o dia porque "
            "a jornada nao esta configurada."
        )

    # --------------------------------------------------------
    # Descanso
    # --------------------------------------------------------

    elif dia.tipo_dia == "descanso":

        if minutos is None:

            resultado[
                "status"
            ] = "descanso"

            resultado[
                "mensagem"
            ] = "Descanso sem marcacoes."

        else:

            horas_efetivas = (
                _minutos_para_horas(
                    minutos
                )
            )

            resultado[
                "status"
            ] = "descanso_trabalhado"

            resultado[
                "horas_extras"
            ] = horas_efetivas

            resultado[
                "saldo_banco_candidato"
            ] = horas_efetivas

            resultado[
                "mensagem"
            ] = (
                "Houve trabalho em dia de descanso. "
                "Saldo positivo pendente de tratamento."
            )

    # --------------------------------------------------------
    # Trabalho previsto
    # --------------------------------------------------------

    elif dia.tipo_dia == "trabalho":

        if minutos is None:

            resultado[
                "status"
            ] = "sem_marcacao"

            resultado[
                "mensagem"
            ] = (
                "Dia de trabalho sem marcacoes. "
                "Ainda nao convertido automaticamente "
                "em falta."
            )

        else:

            horas_efetivas = (
                _minutos_para_horas(
                    minutos
                )
            )

            previstas = (
                dia.horas_previstas
                or zero
            )

            if horas_efetivas >= previstas:

                resultado[
                    "horas_trabalhadas"
                ] = previstas

                resultado[
                    "horas_extras"
                ] = (
                    horas_efetivas
                    - previstas
                ).quantize(
                    Decimal("0.01")
                )

                resultado[
                    "saldo_banco_candidato"
                ] = resultado[
                    "horas_extras"
                ]

                resultado[
                    "status"
                ] = (
                    "com_extra"
                    if resultado[
                        "horas_extras"
                    ] > zero
                    else "regular"
                )

            else:

                resultado[
                    "horas_trabalhadas"
                ] = horas_efetivas

                resultado[
                    "horas_faltas_atrasos"
                ] = (
                    previstas
                    - horas_efetivas
                ).quantize(
                    Decimal("0.01")
                )

                resultado[
                    "saldo_banco_candidato"
                ] = (
                    -resultado[
                        "horas_faltas_atrasos"
                    ]
                )

                resultado[
                    "status"
                ] = "jornada_incompleta"

            resultado[
                "mensagem"
            ] = (
                "Dia de trabalho apurado pelas "
                "marcacoes registradas."
            )

    else:

        raise ValidationError(
            "Tipo de dia desconhecido para apuracao: "
            f"{dia.tipo_dia}."
        )


    from .services_justificativas import (
        aplicar_decisoes_justificativas_apuracao,
    )

    resultado = (
        aplicar_decisoes_justificativas_apuracao(
            dia,
            resultado,
        )
    )

    if salvar:

        dia.horas_trabalhadas = resultado[
            "horas_trabalhadas"
        ]

        dia.horas_extras = resultado[
            "horas_extras"
        ]

        dia.horas_feriado = resultado[
            "horas_feriado"
        ]

        dia.horas_abonadas = resultado[
            "horas_abonadas"
        ]

        dia.horas_compensacao_autorizada = resultado[
            "horas_compensacao_autorizada"
        ]

        dia.horas_faltas_atrasos = resultado[
            "horas_faltas_atrasos"
        ]

        dia.saldo_banco_candidato = resultado[
            "saldo_banco_candidato"
        ]

        dia.save(
            update_fields=[
                "horas_trabalhadas",
                "horas_extras",
                "horas_feriado",
                "horas_abonadas",
                "horas_compensacao_autorizada",
                "horas_faltas_atrasos",
                "saldo_banco_candidato",
                "atualizado_em",
            ]
        )

    return resultado


def apurar_dias_folha_ponto(
    folha_ponto,
):
    """
    Apura todos os dias da competencia.

    Dias sem marcacao permanecem pendentes.
    Nao fecha a folha e nao movimenta banco de horas.
    """
    if folha_ponto.status != "aberta":
        raise ValidationError(
            "Somente folha aberta pode ser apurada."
        )

    resultados = []

    for dia in (
        folha_ponto.dias
        .select_related(
            "ferias",
            "afastamento",
            "afastamento__tipo",
        )
        .order_by(
            "data"
        )
    ):

        try:
            apuracao = (
                apurar_dia_folha_ponto(
                    dia,
                    salvar=True,
                )
            )

            resultados.append(
                {
                    "data": dia.data,
                    "sucesso": True,
                    **apuracao,
                }
            )

        except ValidationError as exc:

            resultados.append(
                {
                    "data": dia.data,
                    "sucesso": False,
                    "status": "inconsistente",
                    "erro": str(exc),
                }
            )

    return {
        "total": len(
            resultados
        ),
        "sucesso": sum(
            1
            for item in resultados
            if item["sucesso"]
        ),
        "inconsistencias": sum(
            1
            for item in resultados
            if not item["sucesso"]
        ),
        "dias": resultados,
    }


# ============================================================
# ETAPA 8.5 - MOTOR INTEGRADO
# PONTO + HORAS EXTRAS + BANCO + FOLHA PAGAMENTO
# ============================================================


def regime_banco_horas_vigente_data(
    funcionario,
    data,
):
    """
    Localiza regime ativo de Banco de Horas
    vigente na data.
    """
    from django.db import models

    from .models import RegimeBancoHoras

    return (
        RegimeBancoHoras.objects
        .filter(
            funcionario=funcionario,
            ativo=True,
            data_inicio__lte=data,
        )
        .filter(
            models.Q(
                data_fim__isnull=True
            )
            | models.Q(
                data_fim__gte=data
            )
        )
        .order_by(
            "-data_inicio",
            "-pk",
        )
        .first()
    )


def saldo_banco_horas_funcionario(
    funcionario,
    ate_data=None,
):
    """
    Reconstrui o saldo auditavel do Banco de Horas
    a partir dos movimentos.
    """
    from .models import MovimentoBancoHoras

    movimentos = (
        MovimentoBancoHoras.objects
        .filter(
            funcionario=funcionario
        )
        .order_by(
            "data",
            "pk",
        )
    )

    if ate_data:
        movimentos = movimentos.filter(
            data__lte=ate_data
        )

    total = ZERO_HORAS

    for movimento in movimentos:
        total += movimento.horas_com_sinal

    return total.quantize(
        Decimal("0.01")
    )


def _referencia_movimento_ponto(
    dia,
):
    """
    Referencia unica para impedir que o mesmo saldo
    diario seja lancado duas vezes.
    """
    return (
        f"diafolhaponto:{dia.pk}"
    )


def _movimentar_banco_horas_dia(
    dia,
    saldo_override=None,
):
    """
    Converte saldo diario em movimento auditavel.

    saldo_override permite movimentar somente a parcela
    expressamente autorizada para compensacao.
    """

    from .models import MovimentoBancoHoras

    saldo = (
        saldo_override
        if saldo_override is not None
        else (
            dia.saldo_banco_candidato
            or ZERO_HORAS
        )
    )

    saldo = Decimal(
        saldo
    ).quantize(
        Decimal("0.01")
    )

    if saldo == ZERO_HORAS:

        dia.tratamento_saldo = "sem_saldo"

        dia.save(
            update_fields=[
                "tratamento_saldo",
                "atualizado_em",
            ]
        )

        return None

    regime = regime_banco_horas_vigente_data(
        dia.funcionario,
        dia.data,
    )

    if not regime:

        raise ValidationError(
            "Nao existe regime de Banco de Horas "
            "vigente para "
            f"{dia.funcionario} em "
            f"{dia.data:%d/%m/%Y}."
        )

    referencia = (
        _referencia_movimento_ponto(
            dia
        )
    )

    tipo = (
        "credito"
        if saldo > ZERO_HORAS
        else "debito"
    )

    horas = abs(
        saldo
    ).quantize(
        Decimal("0.01")
    )

    movimento = (
        MovimentoBancoHoras.objects
        .filter(
            referencia_origem=referencia
        )
        .first()
    )

    if movimento:

        if (
            movimento.funcionario_id
            != dia.funcionario_id
            or movimento.regime_id
            != regime.id
            or movimento.tipo
            != tipo
            or movimento.horas
            != horas
        ):

            raise ValidationError(
                "Ja existe movimento de Banco de Horas "
                "para o dia, mas o valor/origem mudou. "
                "Estorne ou revise antes de reprocessar."
            )

    else:

        movimento = MovimentoBancoHoras(
            funcionario=dia.funcionario,
            regime=regime,
            data=dia.data,
            competencia=(
                dia.folha_ponto.competencia
            ),
            tipo=tipo,
            origem="ponto",
            horas=horas,
            descricao=(
                "Gerado automaticamente pela "
                "apuracao diaria do ponto."
            ),
            referencia_origem=referencia,
        )

        movimento.full_clean()
        movimento.save()

    dia.tratamento_saldo = "banco"

    dia.save(
        update_fields=[
            "tratamento_saldo",
            "atualizado_em",
        ]
    )

    return movimento

def tratar_saldo_dia(
    dia,
    destino_horas_extras="folha",
    usar_banco_para_deficits=False,
):
    """
    Define o destino do saldo diario.

    Para saldo negativo:
    1. decisao expressa de compensacao tem prioridade
       e movimenta somente a parcela autorizada;
    2. sem decisao expressa, preserva-se o comportamento
       legado opcional de Banco de Horas;
    3. o saldo nao destinado ao banco permanece para folha.
    """

    saldo = (
        dia.saldo_banco_candidato
        or ZERO_HORAS
    )

    if saldo == ZERO_HORAS:

        dia.tratamento_saldo = "sem_saldo"

        dia.save(
            update_fields=[
                "tratamento_saldo",
                "atualizado_em",
            ]
        )

        return {
            "destino": "sem_saldo",
            "movimento": None,
        }

    # -----------------------------------------------------
    # SALDO POSITIVO
    # -----------------------------------------------------

    if saldo > ZERO_HORAS:

        if destino_horas_extras == "banco":

            movimento = (
                _movimentar_banco_horas_dia(
                    dia
                )
            )

            return {
                "destino": "banco",
                "movimento": movimento,
            }

        if destino_horas_extras == "folha":

            dia.tratamento_saldo = "folha"

            dia.save(
                update_fields=[
                    "tratamento_saldo",
                    "atualizado_em",
                ]
            )

            return {
                "destino": "folha",
                "movimento": None,
            }

        raise ValidationError(
            "Destino de horas extras invalido. "
            "Use 'folha' ou 'banco'."
        )

    # -----------------------------------------------------
    # SALDO NEGATIVO - COMPENSACAO EXPRESSA
    # -----------------------------------------------------

    autorizada = (
        dia.horas_compensacao_autorizada
        or ZERO_HORAS
    )

    if autorizada > ZERO_HORAS:

        parcela = min(
            abs(saldo),
            autorizada,
        ).quantize(
            Decimal("0.01")
        )

        movimento = (
            _movimentar_banco_horas_dia(
                dia,
                saldo_override=-parcela,
            )
        )

        return {
            "destino": "banco",
            "movimento": movimento,
            "horas_banco": parcela,
            "horas_folha": max(
                (
                    dia.horas_faltas_atrasos
                    or ZERO_HORAS
                )
                - parcela,
                ZERO_HORAS,
            ).quantize(
                Decimal("0.01")
            ),
        }

    # -----------------------------------------------------
    # COMPORTAMENTO LEGADO OPCIONAL
    # -----------------------------------------------------

    if (
        destino_horas_extras == "banco"
        and usar_banco_para_deficits
    ):

        movimento = (
            _movimentar_banco_horas_dia(
                dia
            )
        )

        return {
            "destino": "banco",
            "movimento": movimento,
        }

    dia.tratamento_saldo = "folha"

    dia.save(
        update_fields=[
            "tratamento_saldo",
            "atualizado_em",
        ]
    )

    return {
        "destino": "folha",
        "movimento": None,
    }

def validar_competencia_pronta_para_fechamento(
    folha_ponto,
):
    """
    Impede processamento financeiro quando ainda
    existem dias de trabalho sem marcacao ou
    inconsistencias cadastrais.
    """
    pendencias = []

    for dia in (
        folha_ponto.dias
        .order_by("data")
    ):

        try:
            resultado = (
                apurar_dia_folha_ponto(
                    dia,
                    salvar=True,
                )
            )

        except ValidationError as exc:

            pendencias.append(
                {
                    "data": dia.data,
                    "tipo": "inconsistencia",
                    "mensagem": str(exc),
                }
            )

            continue

        if resultado[
            "status"
        ] == "sem_marcacao":

            pendencias.append(
                {
                    "data": dia.data,
                    "tipo": "sem_marcacao",
                    "mensagem": (
                        "Dia de trabalho sem "
                        "marcacoes."
                    ),
                }
            )

    return pendencias


def horas_falta_para_folha_dia(
    dia,
):
    """
    Retorna somente a parcela do deficit que deve
    permanecer como falta/atraso financeiro na folha.
    """

    deficit = (
        dia.horas_faltas_atrasos
        or ZERO_HORAS
    )

    if deficit <= ZERO_HORAS:

        return ZERO_HORAS

    if (
        dia.tratamento_saldo
        != "banco"
        or dia.saldo_banco_candidato
        >= ZERO_HORAS
    ):

        return deficit.quantize(
            Decimal("0.01")
        )

    autorizada = (
        dia.horas_compensacao_autorizada
        or ZERO_HORAS
    )

    # Movimento legado sem decisao especifica:
    # todo o deficit foi destinado ao banco.
    if autorizada <= ZERO_HORAS:

        return ZERO_HORAS

    return max(
        deficit - autorizada,
        ZERO_HORAS,
    ).quantize(
        Decimal("0.01")
    )


def consolidar_folha_ponto(
    folha_ponto,
    destino_horas_extras="folha",
    usar_banco_para_deficits=False,
):
    """
    Consolida todos os dias da competencia na
    FolhaPonto mensal.
    """
    if folha_ponto.status != "aberta":

        raise ValidationError(
            "Somente folha de ponto aberta "
            "pode ser consolidada."
        )

    gerar_calendario_folha_ponto(
        folha_ponto
    )

    pendencias = (
        validar_competencia_pronta_para_fechamento(
            folha_ponto
        )
    )

    if pendencias:

        resumo = "; ".join(
            f"{item['data']:%d/%m/%Y}: "
            f"{item['mensagem']}"
            for item
            in pendencias[:10]
        )

        if len(
            pendencias
        ) > 10:

            resumo += (
                f"; e mais "
                f"{len(pendencias) - 10} pendencia(s)"
            )

        raise ValidationError(
            "A competencia possui pendencias "
            "e nao pode ser consolidada: "
            + resumo
        )

    for dia in (
        folha_ponto.dias
        .order_by(
            "data"
        )
    ):

        tratar_saldo_dia(
            dia,
            destino_horas_extras=(
                destino_horas_extras
            ),
            usar_banco_para_deficits=(
                usar_banco_para_deficits
            ),
        )

    dias = (
        folha_ponto.dias
        .all()
    )

    horas_previstas = ZERO_HORAS
    horas_abonadas = ZERO_HORAS
    horas_trabalhadas = ZERO_HORAS
    horas_extras_total = ZERO_HORAS
    horas_extras_folha = ZERO_HORAS
    horas_extras_banco = ZERO_HORAS
    horas_faltas_folha = ZERO_HORAS

    for dia in dias:

        horas_previstas += (
            dia.horas_previstas
            or ZERO_HORAS
        )

        horas_abonadas += (
            dia.horas_abonadas
            or ZERO_HORAS
        )

        horas_trabalhadas += (
            dia.horas_trabalhadas
            or ZERO_HORAS
        )

        horas_extras_total += (
            dia.horas_extras
            or ZERO_HORAS
        )

        if (
            dia.saldo_banco_candidato
            > ZERO_HORAS
        ):

            if (
                dia.tratamento_saldo
                == "banco"
            ):
                horas_extras_banco += (
                    dia.horas_extras
                    or ZERO_HORAS
                )

            elif (
                dia.tratamento_saldo
                == "folha"
            ):
                horas_extras_folha += (
                    dia.horas_extras
                    or ZERO_HORAS
                )

        horas_faltas_folha += (
            horas_falta_para_folha_dia(
                dia
            )
        )

    folha_ponto.horas_previstas = (
        horas_previstas.quantize(
            Decimal("0.01")
        )
    )

    folha_ponto.horas_abonadas = (
        horas_abonadas.quantize(
            Decimal("0.01")
        )
    )

    folha_ponto.horas_trabalhadas = (
        horas_trabalhadas.quantize(
            Decimal("0.01")
        )
    )

    folha_ponto.horas_extras = (
        horas_extras_total.quantize(
            Decimal("0.01")
        )
    )

    folha_ponto.horas_extras_folha = (
        horas_extras_folha.quantize(
            Decimal("0.01")
        )
    )

    folha_ponto.horas_extras_banco = (
        horas_extras_banco.quantize(
            Decimal("0.01")
        )
    )

    folha_ponto.horas_faltas_atrasos = (
        horas_faltas_folha.quantize(
            Decimal("0.01")
        )
    )

    folha_ponto.banco_horas = (
        saldo_banco_horas_funcionario(
            folha_ponto.funcionario
        )
    )

    folha_ponto.save(
        update_fields=[
            "horas_previstas",
            "horas_abonadas",
            "horas_trabalhadas",
            "horas_extras",
            "horas_extras_folha",
            "horas_extras_banco",
            "horas_faltas_atrasos",
            "banco_horas",
            "atualizado_em",
        ]
    )

    return folha_ponto


def gerar_ou_atualizar_folha_pagamento(
    folha_ponto,
    adicional_percentual_hora_extra=Decimal(
        "50.00"
    ),
):
    """
    Gera a folha financeira a partir da FolhaPonto
    consolidada.

    INSS, IRRF, beneficios e demais rubricas legais
    permanecem parametrizados; nenhum percentual legal
    variavel e inventado neste motor.
    """
    from .models import FolhaPagamento

    funcionario = folha_ponto.funcionario

    salario_base = (
        funcionario.salarioBase
    )

    if (
        salario_base is None
        or salario_base
        <= ZERO_HORAS
    ):
        raise ValidationError(
            "O colaborador nao possui salario-base "
            "valido para gerar a folha de pagamento."
        )

    folha = (
        FolhaPagamento.objects
        .filter(
            funcionario=funcionario,
            competencia=folha_ponto.competencia,
        )
        .first()
    )

    if folha:

        if folha.status == "fechada":

            raise ValidationError(
                "A folha de pagamento desta "
                "competencia ja esta fechada."
            )

        folha.folha_ponto = (
            folha_ponto
        )

        folha.salario_base = (
            salario_base
        )

        folha.adicional_percentual_hora_extra = (
            adicional_percentual_hora_extra
        )

        folha.full_clean()

        folha.save(
            update_fields=[
                "folha_ponto",
                "salario_base",
                "adicional_percentual_hora_extra",
                "atualizado_em",
            ]
        )

    else:

        folha = FolhaPagamento(
            funcionario=funcionario,
            folha_ponto=folha_ponto,
            competencia=folha_ponto.competencia,
            salario_base=salario_base,
            adicional_percentual_hora_extra=(
                adicional_percentual_hora_extra
            ),
        )

        folha.full_clean()
        folha.save()

    return folha


def resumo_folha_pagamento(
    folha,
):
    """
    Retorna memoria objetiva da folha calculada.
    """
    return {
        "competencia": folha.competencia,
        "salario_base": folha.salario_base,
        "horas_extras_pagas": (
            folha.folha_ponto.horas_extras_folha
            if folha.folha_ponto
            else ZERO_HORAS
        ),
        "horas_extras_banco": (
            folha.folha_ponto.horas_extras_banco
            if folha.folha_ponto
            else ZERO_HORAS
        ),
        "valor_horas_extras": (
            folha.valor_horas_extras
        ),
        "desconto_faltas_atrasos": (
            folha.desconto_faltas_atrasos
        ),
        "total_proventos": (
            folha.total_proventos
        ),
        "total_descontos": (
            folha.total_descontos
        ),
        "valor_liquido": (
            folha.valor_liquido
        ),
    }


def processar_competencia_trabalhista(
    folha_ponto,
    destino_horas_extras="folha",
    usar_banco_para_deficits=False,
    adicional_percentual_hora_extra=Decimal(
        "50.00"
    ),
):
    """
    EXECUCAO INTEGRADA DA COMPETENCIA.

    1. gera/regenera calendario;
    2. considera ferias/licencas/afastamentos;
    3. apura marcacoes;
    4. identifica faltas/atrasos;
    5. identifica horas extras;
    6. destina horas extras a Folha ou Banco;
    7. impede dupla contabilizacao;
    8. consolida FolhaPonto;
    9. gera/atualiza FolhaPagamento;
    10. devolve memoria de calculo.

    A operacao e atomica.
    """
    from django.db import transaction

    with transaction.atomic():

        folha_ponto = (
            consolidar_folha_ponto(
                folha_ponto,
                destino_horas_extras=(
                    destino_horas_extras
                ),
                usar_banco_para_deficits=(
                    usar_banco_para_deficits
                ),
            )
        )

        folha_pagamento = (
            gerar_ou_atualizar_folha_pagamento(
                folha_ponto,
                adicional_percentual_hora_extra=(
                    adicional_percentual_hora_extra
                ),
            )
        )

        resumo = (
            resumo_folha_pagamento(
                folha_pagamento
            )
        )

        return {
            "folha_ponto": folha_ponto,
            "folha_pagamento": folha_pagamento,
            "resumo": resumo,
        }


# ============================================================
# PREENCHIMENTO AUTOMATICO DA JORNADA PADRAO
# ============================================================


def _somar_minutos_horario(
    horario,
    minutos,
):
    """
    Soma minutos a um horario e devolve apenas o time.
    """
    from datetime import date, datetime, timedelta

    base = datetime.combine(
        date(2000, 1, 1),
        horario,
    )

    return (
        base
        + timedelta(
            minutes=minutos
        )
    ).time()


def preencher_jornada_padrao_folha(
    folha_ponto,
):
    """
    Preenche as marcacoes padrao dos dias de trabalho
    usando a JornadaEscala vinculada ao calendario.

    Protecoes:
    - somente dias tipo 'trabalho';
    - nao altera dias com qualquer marcacao existente;
    - nao preenche descanso, ferias ou afastamentos;
    - exige entrada/saida configuradas na jornada;
    - intervalo e posicionado no centro da jornada liquida.

    Exemplo:
    08:00-17:00, 8h previstas, intervalo 60 min
    => 08:00 / 12:00 / 13:00 / 17:00.
    """

    if folha_ponto.status != "aberta":

        raise ValidationError(
            "Somente folha de ponto aberta pode "
            "receber jornada padrao."
        )

    gerar_calendario_folha_ponto(
        folha_ponto
    )

    preenchidos = 0
    preservados = 0
    ignorados = 0
    inconsistencias = []

    dias = (
        folha_ponto.dias
        .select_related(
            "jornada_escala",
        )
        .order_by(
            "data"
        )
    )

    for dia in dias:

        if dia.tipo_dia != "trabalho":

            ignorados += 1
            continue

        # Nunca sobrescrever marcacao manual.
        if any(
            [
                dia.entrada_1,
                dia.saida_1,
                dia.entrada_2,
                dia.saida_2,
            ]
        ):

            preservados += 1
            continue

        jornada = dia.jornada_escala

        if not jornada:

            inconsistencias.append(
                {
                    "data": dia.data,
                    "mensagem": (
                        "Dia de trabalho sem "
                        "jornada de escala vinculada."
                    ),
                }
            )

            continue

        if (
            not jornada.hora_entrada
            or not jornada.hora_saida
        ):

            inconsistencias.append(
                {
                    "data": dia.data,
                    "mensagem": (
                        "Jornada sem horario de "
                        "entrada/saida configurado."
                    ),
                }
            )

            continue

        intervalo = (
            jornada.intervalo_minutos
            or 0
        )

        minutos_previstos = int(
            (
                jornada.horas_previstas
                or ZERO_HORAS
            )
            * Decimal("60")
        )

        if intervalo <= 0:

            dia.entrada_1 = (
                jornada.hora_entrada
            )

            dia.saida_1 = (
                jornada.hora_saida
            )

            dia.entrada_2 = None
            dia.saida_2 = None

        else:

            if minutos_previstos <= 0:

                inconsistencias.append(
                    {
                        "data": dia.data,
                        "mensagem": (
                            "Jornada com intervalo, "
                            "mas sem horas previstas."
                        ),
                    }
                )

                continue

            primeiro_periodo = (
                minutos_previstos // 2
            )

            saida_intervalo = (
                _somar_minutos_horario(
                    jornada.hora_entrada,
                    primeiro_periodo,
                )
            )

            retorno_intervalo = (
                _somar_minutos_horario(
                    saida_intervalo,
                    intervalo,
                )
            )

            dia.entrada_1 = (
                jornada.hora_entrada
            )

            dia.saida_1 = (
                saida_intervalo
            )

            dia.entrada_2 = (
                retorno_intervalo
            )

            dia.saida_2 = (
                jornada.hora_saida
            )

        dia.save(
            update_fields=[
                "entrada_1",
                "saida_1",
                "entrada_2",
                "saida_2",
                "atualizado_em",
            ]
        )

        preenchidos += 1

    return {
        "preenchidos": preenchidos,
        "preservados": preservados,
        "ignorados": ignorados,
        "inconsistencias": inconsistencias,
    }
