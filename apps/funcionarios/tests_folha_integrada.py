from datetime import date, time
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    EscalaFuncionario,
    EscalaTrabalho,
    FolhaPonto,
    Funcionario,
    JornadaEscala,
    MovimentoBancoHoras,
    RegimeBancoHoras,
)
from apps.funcionarios.services import (
    gerar_calendario_folha_ponto,
    processar_competencia_trabalhista,
)


class FolhaIntegradaTests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Folha Integrada",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Folha Integrada",
            usuario="folha-integrada",
            cpf="52998224725",
            empresa=self.empresa,
            data_admissao=date(
                2026,
                10,
                1,
            ),
            salarioBase=Decimal(
                "2200.00"
            ),
            divisor_mensal=220,
        )

        self.escala = EscalaTrabalho.objects.create(
            empresa=self.empresa,
            nome="5x2 Integrada",
            tipo="5x2",
            ciclo_dias=7,
            jornada_semanal_referencia=Decimal(
                "40.00"
            ),
            data_inicio=date(
                2026,
                1,
                1,
            ),
        )

        for posicao in range(
            1,
            8,
        ):

            JornadaEscala.objects.create(
                escala=self.escala,
                posicao_ciclo=posicao,
                trabalha=(
                    posicao <= 5
                ),
                horas_previstas=(
                    Decimal("8.00")
                    if posicao <= 5
                    else Decimal("0.00")
                ),
                intervalo_minutos=(
                    60
                    if posicao <= 5
                    else 0
                ),
            )

        EscalaFuncionario.objects.create(
            funcionario=self.funcionario,
            escala=self.escala,
            data_inicio=date(
                2026,
                10,
                1,
            ),
            data_referencia=date(
                2026,
                10,
                1,
            ),
        )

        self.folha_ponto = FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(
                2026,
                10,
                1,
            ),
        )

        gerar_calendario_folha_ponto(
            self.folha_ponto
        )

    def preencher_dias_regulares(
        self,
        extra_primeiro_dia=False,
    ):

        dias = (
            self.folha_ponto.dias
            .filter(
                tipo_dia="trabalho"
            )
            .order_by(
                "data"
            )
        )

        primeiro = True

        for dia in dias:

            dia.entrada_1 = time(
                8,
                0,
            )

            dia.saida_1 = time(
                12,
                0,
            )

            dia.entrada_2 = time(
                13,
                0,
            )

            if (
                primeiro
                and extra_primeiro_dia
            ):
                dia.saida_2 = time(
                    18,
                    0,
                )

            else:
                dia.saida_2 = time(
                    17,
                    0,
                )

            dia.save()

            primeiro = False

    def test_processa_ponto_e_folha_com_hora_extra(
        self
    ):

        self.preencher_dias_regulares(
            extra_primeiro_dia=True
        )

        resultado = (
            processar_competencia_trabalhista(
                self.folha_ponto,
                destino_horas_extras="folha",
            )
        )

        ponto = resultado[
            "folha_ponto"
        ]

        folha = resultado[
            "folha_pagamento"
        ]

        self.assertEqual(
            ponto.horas_extras,
            Decimal("1.00"),
        )

        self.assertEqual(
            ponto.horas_extras_folha,
            Decimal("1.00"),
        )

        self.assertEqual(
            ponto.horas_extras_banco,
            Decimal("0.00"),
        )

        # 2200 / 220 = 10,00
        # HE 50% = 15,00
        self.assertEqual(
            folha.valor_horas_extras,
            Decimal("15.00"),
        )

        self.assertEqual(
            folha.total_proventos,
            Decimal("2215.00"),
        )

    def test_hora_extra_para_banco_nao_e_paga(
        self
    ):

        RegimeBancoHoras.objects.create(
            funcionario=self.funcionario,
            tipo="individual_6m",
            data_inicio=date(
                2026,
                1,
                1,
            ),
            prazo_compensacao_meses=6,
            referencia_documento=(
                "Acordo individual teste"
            ),
        )

        self.preencher_dias_regulares(
            extra_primeiro_dia=True
        )

        resultado = (
            processar_competencia_trabalhista(
                self.folha_ponto,
                destino_horas_extras="banco",
            )
        )

        ponto = resultado[
            "folha_ponto"
        ]

        folha = resultado[
            "folha_pagamento"
        ]

        self.assertEqual(
            ponto.horas_extras,
            Decimal("1.00"),
        )

        self.assertEqual(
            ponto.horas_extras_folha,
            Decimal("0.00"),
        )

        self.assertEqual(
            ponto.horas_extras_banco,
            Decimal("1.00"),
        )

        self.assertEqual(
            folha.valor_horas_extras,
            Decimal("0.00"),
        )

        self.assertEqual(
            MovimentoBancoHoras.objects.count(),
            1,
        )

        movimento = (
            MovimentoBancoHoras.objects.get()
        )

        self.assertEqual(
            movimento.tipo,
            "credito",
        )

        self.assertEqual(
            movimento.horas,
            Decimal("1.00"),
        )

    def test_reprocessamento_nao_duplica_banco(
        self
    ):

        RegimeBancoHoras.objects.create(
            funcionario=self.funcionario,
            tipo="individual_6m",
            data_inicio=date(
                2026,
                1,
                1,
            ),
            prazo_compensacao_meses=6,
        )

        self.preencher_dias_regulares(
            extra_primeiro_dia=True
        )

        processar_competencia_trabalhista(
            self.folha_ponto,
            destino_horas_extras="banco",
        )

        processar_competencia_trabalhista(
            self.folha_ponto,
            destino_horas_extras="banco",
        )

        self.assertEqual(
            MovimentoBancoHoras.objects.count(),
            1,
        )

    def test_sem_marcacao_bloqueia_folha(
        self
    ):

        with self.assertRaises(
            ValidationError
        ):
            processar_competencia_trabalhista(
                self.folha_ponto,
                destino_horas_extras="folha",
            )

    def test_falta_parcial_vai_para_desconto(
        self
    ):

        self.preencher_dias_regulares()

        primeiro = (
            self.folha_ponto.dias
            .filter(
                tipo_dia="trabalho"
            )
            .order_by(
                "data"
            )
            .first()
        )

        primeiro.saida_2 = time(
            16,
            0,
        )

        primeiro.save(
            update_fields=[
                "saida_2",
            ]
        )

        resultado = (
            processar_competencia_trabalhista(
                self.folha_ponto,
                destino_horas_extras="folha",
            )
        )

        ponto = resultado[
            "folha_ponto"
        ]

        folha = resultado[
            "folha_pagamento"
        ]

        self.assertEqual(
            ponto.horas_faltas_atrasos,
            Decimal("1.00"),
        )

        self.assertEqual(
            folha.desconto_faltas_atrasos,
            Decimal("10.00"),
        )

    def test_folha_e_gerada_uma_unica_vez(
        self
    ):

        self.preencher_dias_regulares()

        primeiro = (
            processar_competencia_trabalhista(
                self.folha_ponto,
                destino_horas_extras="folha",
            )
        )

        segundo = (
            processar_competencia_trabalhista(
                self.folha_ponto,
                destino_horas_extras="folha",
            )
        )

        self.assertEqual(
            primeiro[
                "folha_pagamento"
            ].pk,
            segundo[
                "folha_pagamento"
            ].pk,
        )

        self.assertEqual(
            self.funcionario
            .folhas_pagamento
            .count(),
            1,
        )
