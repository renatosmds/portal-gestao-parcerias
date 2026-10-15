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
)
from apps.funcionarios.services import (
    apurar_jornada_prevista_data,
    horas_previstas_competencia_escala,
    horas_previstas_periodo,
    posicao_ciclo_escala,
)


class MotorEscalasTests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Motor Escalas",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Motor",
            usuario="motor",
            cpf="52998224725",
            empresa=self.empresa,
            salarioBase=Decimal(
                "3000.00"
            ),
            data_admissao=date(
                2026,
                10,
                1,
            ),
        )

    def criar_escala(
        self,
        nome,
        tipo,
        ciclo,
        jornadas,
        inicio=date(
            2026,
            1,
            1,
        ),
    ):

        escala = EscalaTrabalho.objects.create(
            empresa=self.empresa,
            nome=nome,
            tipo=tipo,
            ciclo_dias=ciclo,
            data_inicio=inicio,
        )

        for (
            posicao,
            trabalha,
            horas,
        ) in jornadas:

            JornadaEscala.objects.create(
                escala=escala,
                posicao_ciclo=posicao,
                trabalha=trabalha,
                horas_previstas=Decimal(
                    horas
                ),
            )

        return escala

    def vincular(
        self,
        escala,
        inicio=date(
            2026,
            10,
            1,
        ),
        referencia=date(
            2026,
            10,
            1,
        ),
        fim=None,
    ):

        return EscalaFuncionario.objects.create(
            funcionario=self.funcionario,
            escala=escala,
            data_inicio=inicio,
            data_fim=fim,
            data_referencia=referencia,
        )

    def test_posicao_do_ciclo(self):

        escala = self.criar_escala(
            "5x2",
            "5x2",
            7,
            [
                (1, True, "8.00"),
                (2, True, "8.00"),
                (3, True, "8.00"),
                (4, True, "8.00"),
                (5, True, "8.00"),
                (6, False, "0.00"),
                (7, False, "0.00"),
            ],
        )

        vinculo = self.vincular(
            escala
        )

        self.assertEqual(
            posicao_ciclo_escala(
                vinculo,
                date(
                    2026,
                    10,
                    1,
                ),
            ),
            1,
        )

        self.assertEqual(
            posicao_ciclo_escala(
                vinculo,
                date(
                    2026,
                    10,
                    8,
                ),
            ),
            1,
        )

    def test_5x2_trabalho_e_descanso(self):

        escala = self.criar_escala(
            "5x2 - 40h",
            "5x2",
            7,
            [
                (1, True, "8.00"),
                (2, True, "8.00"),
                (3, True, "8.00"),
                (4, True, "8.00"),
                (5, True, "8.00"),
                (6, False, "0.00"),
                (7, False, "0.00"),
            ],
        )

        self.vincular(
            escala
        )

        trabalho = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    1,
                ),
            )
        )

        descanso = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    6,
                ),
            )
        )

        self.assertTrue(
            trabalho["trabalha"]
        )

        self.assertEqual(
            trabalho[
                "horas_previstas"
            ],
            Decimal("8.00"),
        )

        self.assertFalse(
            descanso["trabalha"]
        )

        self.assertEqual(
            descanso[
                "horas_previstas"
            ],
            Decimal("0.00"),
        )

    def test_6x1(self):

        escala = self.criar_escala(
            "6x1",
            "6x1",
            7,
            [
                (1, True, "7.33"),
                (2, True, "7.33"),
                (3, True, "7.33"),
                (4, True, "7.33"),
                (5, True, "7.33"),
                (6, True, "7.35"),
                (7, False, "0.00"),
            ],
        )

        self.vincular(
            escala
        )

        for dia in range(
            1,
            7,
        ):
            resultado = (
                apurar_jornada_prevista_data(
                    self.funcionario,
                    date(
                        2026,
                        10,
                        dia,
                    ),
                )
            )

            self.assertTrue(
                resultado["trabalha"]
            )

        descanso = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    7,
                ),
            )
        )

        self.assertFalse(
            descanso["trabalha"]
        )

    def test_12x36_alterna_trabalho_descanso(
        self
    ):

        escala = self.criar_escala(
            "12x36",
            "12x36",
            2,
            [
                (1, True, "12.00"),
                (2, False, "0.00"),
            ],
        )

        self.vincular(
            escala
        )

        dia1 = apurar_jornada_prevista_data(
            self.funcionario,
            date(
                2026,
                10,
                1,
            ),
        )

        dia2 = apurar_jornada_prevista_data(
            self.funcionario,
            date(
                2026,
                10,
                2,
            ),
        )

        dia3 = apurar_jornada_prevista_data(
            self.funcionario,
            date(
                2026,
                10,
                3,
            ),
        )

        self.assertTrue(
            dia1["trabalha"]
        )

        self.assertFalse(
            dia2["trabalha"]
        )

        self.assertTrue(
            dia3["trabalha"]
        )

        self.assertEqual(
            dia1["horas_previstas"],
            Decimal("12.00"),
        )

    def test_admissao_limita_apuracao(self):

        escala = self.criar_escala(
            "Todos os dias teste",
            "personalizada",
            1,
            [
                (1, True, "8.00"),
            ],
        )

        self.funcionario.data_admissao = date(
            2026,
            10,
            10,
        )

        self.funcionario.save(
            update_fields=[
                "data_admissao"
            ]
        )

        self.vincular(
            escala,
            inicio=date(
                2026,
                10,
                10,
            ),
            referencia=date(
                2026,
                10,
                10,
            ),
        )

        antes = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    9,
                ),
            )
        )

        depois = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    10,
                ),
            )
        )

        self.assertFalse(
            antes[
                "em_periodo_contratual"
            ]
        )

        self.assertTrue(
            depois["trabalha"]
        )

    def test_desligamento_limita_apuracao(self):

        escala = self.criar_escala(
            "Escala desligamento",
            "personalizada",
            1,
            [
                (1, True, "8.00"),
            ],
        )

        self.funcionario.data_desligamento = (
            date(
                2026,
                10,
                15,
            )
        )

        self.funcionario.save(
            update_fields=[
                "data_desligamento"
            ]
        )

        self.vincular(
            escala
        )

        ultimo = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    15,
                ),
            )
        )

        posterior = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    16,
                ),
            )
        )

        self.assertTrue(
            ultimo["trabalha"]
        )

        self.assertFalse(
            posterior[
                "em_periodo_contratual"
            ]
        )

    def test_sem_escala_nao_inventa_jornada(
        self
    ):

        resultado = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    10,
                ),
            )
        )

        self.assertFalse(
            resultado["configurada"]
        )

        self.assertEqual(
            resultado[
                "horas_previstas"
            ],
            Decimal("0.00"),
        )

        self.assertEqual(
            resultado["motivo"],
            "escala_nao_configurada",
        )

    def test_periodo_sem_escala_interrompe_calculo(
        self
    ):

        with self.assertRaises(
            ValidationError
        ):
            horas_previstas_periodo(
                self.funcionario,
                date(
                    2026,
                    10,
                    1,
                ),
                date(
                    2026,
                    10,
                    31,
                ),
            )

    def test_mudanca_de_escala_no_mes(self):

        escala1 = self.criar_escala(
            "Escala primeira metade",
            "personalizada",
            1,
            [
                (1, True, "8.00"),
            ],
        )

        escala2 = self.criar_escala(
            "Escala segunda metade",
            "personalizada",
            1,
            [
                (1, True, "6.00"),
            ],
        )

        self.vincular(
            escala1,
            inicio=date(
                2026,
                10,
                1,
            ),
            referencia=date(
                2026,
                10,
                1,
            ),
            fim=date(
                2026,
                10,
                15,
            ),
        )

        self.vincular(
            escala2,
            inicio=date(
                2026,
                10,
                16,
            ),
            referencia=date(
                2026,
                10,
                16,
            ),
        )

        dia15 = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    15,
                ),
            )
        )

        dia16 = (
            apurar_jornada_prevista_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    16,
                ),
            )
        )

        self.assertEqual(
            dia15[
                "horas_previstas"
            ],
            Decimal("8.00"),
        )

        self.assertEqual(
            dia16[
                "horas_previstas"
            ],
            Decimal("6.00"),
        )

    def test_competencia_com_escala_completa(
        self
    ):

        escala = self.criar_escala(
            "Escala 8h diaria",
            "personalizada",
            1,
            [
                (1, True, "8.00"),
            ],
        )

        self.vincular(
            escala
        )

        resultado = (
            horas_previstas_competencia_escala(
                self.funcionario,
                date(
                    2026,
                    10,
                    1,
                ),
            )
        )

        self.assertEqual(
            resultado[
                "dias_trabalho"
            ],
            31,
        )

        self.assertEqual(
            resultado[
                "horas_previstas"
            ],
            Decimal("248.00"),
        )
