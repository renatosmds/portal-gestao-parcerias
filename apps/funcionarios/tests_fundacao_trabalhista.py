from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    EscalaFuncionario,
    EscalaTrabalho,
    Funcionario,
    JornadaEscala,
    MovimentoBancoHoras,
    RegimeBancoHoras,
    VinculoParceria,
)
from apps.termos.models import Termos


class FundacaoTrabalhistaTests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Teste Trabalhista",
        )

        self.termo = Termos.objects.create(
            termo="TC 001/2026",
            empresa=self.empresa,
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Teste",
            usuario="colaborador",
            cpf="52998224725",
            empresa=self.empresa,
            salarioBase=Decimal("3000.00"),
            data_admissao=date(
                2026,
                1,
                1,
            ),
        )

    def test_vinculo_parceria_com_rateio(self):
        vinculo = VinculoParceria(
            funcionario=self.funcionario,
            termo=self.termo,
            data_inicio=date(
                2026,
                1,
                1,
            ),
            percentual_rateio=Decimal(
                "60.000"
            ),
        )

        vinculo.full_clean()
        vinculo.save()

        self.assertEqual(
            vinculo.percentual_rateio,
            Decimal("60.000"),
        )

    def test_rateio_superior_a_100_e_invalido(self):
        vinculo = VinculoParceria(
            funcionario=self.funcionario,
            termo=self.termo,
            data_inicio=date(
                2026,
                1,
                1,
            ),
            percentual_rateio=Decimal(
                "110.000"
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            vinculo.full_clean()

    def test_cria_escala_6x1(self):
        escala = EscalaTrabalho.objects.create(
            empresa=self.empresa,
            nome="Escala 6x1 - 44h",
            tipo="6x1",
            ciclo_dias=7,
            jornada_semanal_referencia=(
                Decimal("44.00")
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
                escala=escala,
                posicao_ciclo=posicao,
                trabalha=(
                    posicao <= 6
                ),
                horas_previstas=(
                    Decimal("7.33")
                    if posicao <= 6
                    else Decimal("0.00")
                ),
            )

        self.assertEqual(
            escala.jornadas_ciclo.count(),
            7,
        )

    def test_cria_escala_12x36(self):
        escala = EscalaTrabalho.objects.create(
            empresa=self.empresa,
            nome="Escala 12x36",
            tipo="12x36",
            ciclo_dias=2,
            data_inicio=date(
                2026,
                1,
                1,
            ),
        )

        JornadaEscala.objects.create(
            escala=escala,
            posicao_ciclo=1,
            trabalha=True,
            horas_previstas=Decimal(
                "12.00"
            ),
        )

        JornadaEscala.objects.create(
            escala=escala,
            posicao_ciclo=2,
            trabalha=False,
            horas_previstas=Decimal(
                "0.00"
            ),
        )

        self.assertEqual(
            escala.jornadas_ciclo.count(),
            2,
        )

    def test_posicao_superior_ao_ciclo_e_invalida(
        self
    ):
        escala = EscalaTrabalho.objects.create(
            empresa=self.empresa,
            nome="Escala teste",
            tipo="personalizada",
            ciclo_dias=2,
            data_inicio=date(
                2026,
                1,
                1,
            ),
        )

        jornada = JornadaEscala(
            escala=escala,
            posicao_ciclo=3,
            trabalha=True,
            horas_previstas=Decimal(
                "8.00"
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            jornada.full_clean()

    def test_vincula_escala_ao_funcionario(self):
        escala = EscalaTrabalho.objects.create(
            empresa=self.empresa,
            nome="5x2 - 40h",
            tipo="5x2",
            ciclo_dias=7,
            jornada_semanal_referencia=(
                Decimal("40.00")
            ),
            data_inicio=date(
                2026,
                1,
                1,
            ),
        )

        vinculo = EscalaFuncionario(
            funcionario=self.funcionario,
            escala=escala,
            data_inicio=date(
                2026,
                1,
                1,
            ),
            data_referencia=date(
                2026,
                1,
                5,
            ),
        )

        vinculo.full_clean()
        vinculo.save()

        self.assertEqual(
            vinculo.funcionario,
            self.funcionario,
        )

    def test_banco_individual_limita_seis_meses(
        self
    ):
        regime = RegimeBancoHoras(
            funcionario=self.funcionario,
            tipo="individual_6m",
            data_inicio=date(
                2026,
                1,
                1,
            ),
            prazo_compensacao_meses=7,
        )

        with self.assertRaises(
            ValidationError
        ):
            regime.full_clean()

    def test_movimento_banco_horas_com_sinal(self):
        regime = RegimeBancoHoras.objects.create(
            funcionario=self.funcionario,
            tipo="individual_6m",
            data_inicio=date(
                2026,
                1,
                1,
            ),
            prazo_compensacao_meses=6,
        )

        credito = MovimentoBancoHoras.objects.create(
            funcionario=self.funcionario,
            regime=regime,
            data=date(
                2026,
                10,
                10,
            ),
            competencia=date(
                2026,
                10,
                1,
            ),
            tipo="credito",
            origem="ponto",
            horas=Decimal(
                "2.50"
            ),
        )

        debito = MovimentoBancoHoras.objects.create(
            funcionario=self.funcionario,
            regime=regime,
            data=date(
                2026,
                10,
                15,
            ),
            competencia=date(
                2026,
                10,
                1,
            ),
            tipo="debito",
            origem="compensacao",
            horas=Decimal(
                "1.00"
            ),
        )

        self.assertEqual(
            credito.horas_com_sinal,
            Decimal("2.50"),
        )

        self.assertEqual(
            debito.horas_com_sinal,
            Decimal("-1.00"),
        )

    def test_competencia_deve_ser_primeiro_dia(
        self
    ):
        regime = RegimeBancoHoras.objects.create(
            funcionario=self.funcionario,
            tipo="mesmo_mes",
            data_inicio=date(
                2026,
                1,
                1,
            ),
        )

        movimento = MovimentoBancoHoras(
            funcionario=self.funcionario,
            regime=regime,
            data=date(
                2026,
                10,
                20,
            ),
            competencia=date(
                2026,
                10,
                20,
            ),
            tipo="credito",
            origem="ponto",
            horas=Decimal(
                "1.00"
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            movimento.full_clean()
