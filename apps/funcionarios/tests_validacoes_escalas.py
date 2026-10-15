from datetime import date, time
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
    validar_escala_trabalhista,
)


class ValidacoesEscalasTests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Validacao Escalas",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Validacao",
            usuario="validacao",
            cpf="52998224725",
            empresa=self.empresa,
            data_admissao=date(
                2026,
                1,
                1,
            ),
        )

    def escala(
        self,
        nome="Escala",
        tipo="personalizada",
        ciclo=7,
        referencia=None,
    ):

        return EscalaTrabalho.objects.create(
            empresa=self.empresa,
            nome=nome,
            tipo=tipo,
            ciclo_dias=ciclo,
            jornada_semanal_referencia=referencia,
            data_inicio=date(
                2026,
                1,
                1,
            ),
        )

    def jornada(
        self,
        escala,
        posicao,
        trabalha,
        horas,
        entrada=None,
        saida=None,
        intervalo=0,
    ):

        return JornadaEscala.objects.create(
            escala=escala,
            posicao_ciclo=posicao,
            trabalha=trabalha,
            horas_previstas=Decimal(
                horas
            ),
            hora_entrada=entrada,
            hora_saida=saida,
            intervalo_minutos=intervalo,
        )

    def test_5x2_valida(self):

        escala = self.escala(
            nome="5x2 40h",
            tipo="5x2",
            ciclo=7,
            referencia=Decimal(
                "40.00"
            ),
        )

        for posicao in range(
            1,
            8,
        ):
            self.jornada(
                escala,
                posicao,
                posicao <= 5,
                (
                    "8.00"
                    if posicao <= 5
                    else "0.00"
                ),
                intervalo=(
                    60
                    if posicao <= 5
                    else 0
                ),
            )

        resultado = (
            validar_escala_trabalhista(
                escala
            )
        )

        self.assertTrue(
            resultado["valida"]
        )

        self.assertEqual(
            resultado["erros"],
            [],
        )

    def test_6x1_valida(self):

        escala = self.escala(
            nome="6x1 44h",
            tipo="6x1",
            ciclo=7,
            referencia=Decimal(
                "44.00"
            ),
        )

        horas = [
            "7.33",
            "7.33",
            "7.33",
            "7.33",
            "7.33",
            "7.35",
            "0.00",
        ]

        for posicao, valor in enumerate(
            horas,
            start=1,
        ):
            self.jornada(
                escala,
                posicao,
                posicao <= 6,
                valor,
                intervalo=(
                    60
                    if posicao <= 6
                    else 0
                ),
            )

        resultado = (
            validar_escala_trabalhista(
                escala
            )
        )

        self.assertTrue(
            resultado["valida"]
        )

    def test_12x36_valida(self):

        escala = self.escala(
            nome="12x36",
            tipo="12x36",
            ciclo=2,
        )

        self.jornada(
            escala,
            1,
            True,
            "12.00",
            intervalo=60,
        )

        self.jornada(
            escala,
            2,
            False,
            "0.00",
        )

        resultado = (
            validar_escala_trabalhista(
                escala
            )
        )

        self.assertTrue(
            resultado["valida"]
        )

    def test_ciclo_incompleto_e_invalido(self):

        escala = self.escala(
            tipo="5x2",
            ciclo=7,
        )

        for posicao in range(
            1,
            6,
        ):
            self.jornada(
                escala,
                posicao,
                True,
                "8.00",
                intervalo=60,
            )

        resultado = (
            validar_escala_trabalhista(
                escala
            )
        )

        self.assertFalse(
            resultado["valida"]
        )

        self.assertTrue(
            any(
                "Ciclo incompleto"
                in erro
                for erro
                in resultado["erros"]
            )
        )

    def test_5x2_com_seis_dias_e_invalida(
        self
    ):

        escala = self.escala(
            tipo="5x2",
            ciclo=7,
        )

        for posicao in range(
            1,
            8,
        ):
            self.jornada(
                escala,
                posicao,
                posicao <= 6,
                (
                    "8.00"
                    if posicao <= 6
                    else "0.00"
                ),
                intervalo=(
                    60
                    if posicao <= 6
                    else 0
                ),
            )

        resultado = (
            validar_escala_trabalhista(
                escala
            )
        )

        self.assertFalse(
            resultado["valida"]
        )

    def test_jornada_acima_de_oito_gera_alerta(
        self
    ):

        escala = self.escala(
            tipo="personalizada",
            ciclo=2,
        )

        self.jornada(
            escala,
            1,
            True,
            "9.00",
            intervalo=60,
        )

        self.jornada(
            escala,
            2,
            False,
            "0.00",
        )

        resultado = (
            validar_escala_trabalhista(
                escala
            )
        )

        self.assertTrue(
            resultado["valida"]
        )

        self.assertTrue(
            any(
                "supera 8 horas"
                in alerta
                for alerta
                in resultado["alertas"]
            )
        )

    def test_intervalo_insuficiente_gera_alerta(
        self
    ):

        escala = self.escala(
            tipo="personalizada",
            ciclo=2,
        )

        self.jornada(
            escala,
            1,
            True,
            "8.00",
            intervalo=30,
        )

        self.jornada(
            escala,
            2,
            False,
            "0.00",
        )

        resultado = (
            validar_escala_trabalhista(
                escala
            )
        )

        self.assertTrue(
            any(
                "intervalo cadastrado"
                in alerta
                for alerta
                in resultado["alertas"]
            )
        )

    def test_horario_incompativel_com_horas_previstas(
        self
    ):

        escala = self.escala(
            tipo="personalizada",
            ciclo=2,
        )

        self.jornada(
            escala,
            1,
            True,
            "8.00",
            entrada=time(
                8,
                0,
            ),
            saida=time(
                18,
                0,
            ),
            intervalo=60,
        )

        self.jornada(
            escala,
            2,
            False,
            "0.00",
        )

        resultado = (
            validar_escala_trabalhista(
                escala
            )
        )

        self.assertFalse(
            resultado["valida"]
        )

        self.assertTrue(
            any(
                "horario informado"
                in erro
                for erro
                in resultado["erros"]
            )
        )

    def test_interjornada_inferior_a_11h_e_invalida(
        self
    ):

        escala = self.escala(
            tipo="personalizada",
            ciclo=3,
        )

        self.jornada(
            escala,
            1,
            True,
            "8.00",
            entrada=time(
                14,
                0,
            ),
            saida=time(
                23,
                0,
            ),
            intervalo=60,
        )

        self.jornada(
            escala,
            2,
            True,
            "8.00",
            entrada=time(
                7,
                0,
            ),
            saida=time(
                16,
                0,
            ),
            intervalo=60,
        )

        self.jornada(
            escala,
            3,
            False,
            "0.00",
        )

        resultado = (
            validar_escala_trabalhista(
                escala
            )
        )

        self.assertFalse(
            resultado["valida"]
        )

        self.assertTrue(
            any(
                "inferior a 11 horas"
                in erro
                for erro
                in resultado["erros"]
            )
        )

    def test_impede_sobreposicao_de_escalas(
        self
    ):

        escala1 = self.escala(
            nome="Escala A",
            ciclo=1,
        )

        escala2 = self.escala(
            nome="Escala B",
            ciclo=1,
        )

        EscalaFuncionario.objects.create(
            funcionario=self.funcionario,
            escala=escala1,
            data_inicio=date(
                2026,
                1,
                1,
            ),
            data_fim=date(
                2026,
                6,
                30,
            ),
            data_referencia=date(
                2026,
                1,
                1,
            ),
        )

        segundo = EscalaFuncionario(
            funcionario=self.funcionario,
            escala=escala2,
            data_inicio=date(
                2026,
                6,
                1,
            ),
            data_fim=date(
                2026,
                12,
                31,
            ),
            data_referencia=date(
                2026,
                6,
                1,
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            segundo.full_clean()

    def test_escalas_sequenciais_sao_permitidas(
        self
    ):

        escala1 = self.escala(
            nome="Escala antiga",
            ciclo=1,
        )

        escala2 = self.escala(
            nome="Escala nova",
            ciclo=1,
        )

        EscalaFuncionario.objects.create(
            funcionario=self.funcionario,
            escala=escala1,
            data_inicio=date(
                2026,
                1,
                1,
            ),
            data_fim=date(
                2026,
                6,
                30,
            ),
            data_referencia=date(
                2026,
                1,
                1,
            ),
        )

        segundo = EscalaFuncionario(
            funcionario=self.funcionario,
            escala=escala2,
            data_inicio=date(
                2026,
                7,
                1,
            ),
            data_referencia=date(
                2026,
                7,
                1,
            ),
        )

        segundo.full_clean()
        segundo.save()

        self.assertIsNotNone(
            segundo.pk
        )
