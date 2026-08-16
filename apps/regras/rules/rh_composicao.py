from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


def _d(valor):
    return Decimal(str(valor or 0)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


@dataclass(frozen=True)
class ComposicaoDespesaRH:
    salario_base: Decimal
    horas_extras: Decimal
    outras_verbas: Decimal
    total_proventos: Decimal

    faltas_atrasos: Decimal
    inss: Decimal
    irrf: Decimal
    vale_transporte: Decimal
    pensao: Decimal
    outros_descontos: Decimal
    total_descontos: Decimal

    valor_liquido: Decimal

    fgts: Decimal
    aviso_previo: Decimal
    ferias_proporcionais: Decimal
    terco_ferias: Decimal
    decimo_terceiro: Decimal
    multa_fgts: Decimal
    verbas_rescisorias: Decimal

    encargos_patronais_identificados: Decimal
    verbas_rescisorias_identificadas: Decimal

    valor_potencialmente_elegivel: Decimal


def calcular_composicao_despesa_rh(folha):
    funcionario = folha.funcionario

    salario_base = _d(
        folha.salario_base
    )

    horas_extras = _d(
        folha.valor_horas_extras
    )

    outras_verbas = _d(
        folha.outras_verbas
    )

    total_proventos = _d(
        folha.total_proventos
    )

    faltas_atrasos = _d(
        folha.desconto_faltas_atrasos
    )

    inss = _d(
        folha.inss
    )

    irrf = _d(
        folha.irrf
    )

    vale_transporte = _d(
        folha.vale_transporte
    )

    pensao = _d(
        folha.pensao
    )

    outros_descontos = _d(
        folha.outros_descontos
    )

    total_descontos = _d(
        folha.total_descontos
    )

    valor_liquido = _d(
        folha.valor_liquido
    )

    fgts = _d(
        getattr(
            funcionario,
            "fgts",
            None,
        )
    )

    aviso_previo = _d(
        getattr(
            funcionario,
            "avisoPrevio",
            None,
        )
    )

    ferias_proporcionais = _d(
        getattr(
            funcionario,
            "avosFerias",
            None,
        )
    )

    terco_ferias = _d(
        getattr(
            funcionario,
            "avosTercoFerias",
            None,
        )
    )

    decimo_terceiro = _d(
        getattr(
            funcionario,
            "avos13Salario",
            None,
        )
    )

    multa_fgts = _d(
        getattr(
            funcionario,
            "multafgts",
            None,
        )
    )

    verbas_rescisorias = _d(
        getattr(
            funcionario,
            "totalVerbaRescisoria",
            None,
        )
    )

    encargos_patronais_identificados = _d(
        fgts
    )

    verbas_rescisorias_identificadas = _d(
        aviso_previo
        + ferias_proporcionais
        + terco_ferias
        + decimo_terceiro
        + multa_fgts
        + verbas_rescisorias
    )

    # ---------------------------------------------------------
    # Valor potencialmente elegível
    #
    # Não representa aprovação administrativa.
    #
    # Parte do total de proventos, desconta faltas/atrasos e
    # soma apenas encargos/verbas adicionais identificados no
    # modelo atual.
    #
    # INSS, IRRF, VT, pensão e outros descontos não são somados
    # como custo adicional aqui, pois já integram a estrutura
    # financeira da folha e exigem tratamento normativo próprio.
    # ---------------------------------------------------------
    valor_potencialmente_elegivel = _d(
        total_proventos
        - faltas_atrasos
        + encargos_patronais_identificados
        + verbas_rescisorias_identificadas
    )

    return ComposicaoDespesaRH(
        salario_base=salario_base,
        horas_extras=horas_extras,
        outras_verbas=outras_verbas,
        total_proventos=total_proventos,

        faltas_atrasos=faltas_atrasos,
        inss=inss,
        irrf=irrf,
        vale_transporte=vale_transporte,
        pensao=pensao,
        outros_descontos=outros_descontos,
        total_descontos=total_descontos,

        valor_liquido=valor_liquido,

        fgts=fgts,
        aviso_previo=aviso_previo,
        ferias_proporcionais=ferias_proporcionais,
        terco_ferias=terco_ferias,
        decimo_terceiro=decimo_terceiro,
        multa_fgts=multa_fgts,
        verbas_rescisorias=verbas_rescisorias,

        encargos_patronais_identificados=(
            encargos_patronais_identificados
        ),

        verbas_rescisorias_identificadas=(
            verbas_rescisorias_identificadas
        ),

        valor_potencialmente_elegivel=(
            valor_potencialmente_elegivel
        ),
    )
