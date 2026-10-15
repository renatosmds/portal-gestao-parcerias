from datetime import date, time
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    AfastamentoFuncionario,
    EscalaFuncionario,
    EscalaTrabalho,
    FeriasFuncionario,
    FolhaPonto,
    Funcionario,
    JornadaEscala,
    PeriodoAquisitivoFerias,
    TipoAfastamento,
)
from apps.funcionarios.services import (
    apurar_dia_folha_ponto,
    gerar_calendario_folha_ponto,
)


class ApuracaoDiariaTests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Apuracao Diaria",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Apuracao",
            usuario="apuracao",
            cpf="52998224725",
            empresa=self.empresa,
            data_admissao=date(
                2026,
                10,
                1,
            ),
        )

        self.escala = EscalaTrabalho.objects.create(
            empresa=self.empresa,
            nome="5x2 8h",
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

        self.folha = FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(
                2026,
                10,
                1,
            ),
        )

        gerar_calendario_folha_ponto(
            self.folha
        )

    def dia(
        self,
        numero,
    ):
        return self.folha.dias.get(
            data=date(
                2026,
                10,
                numero,
            )
        )

    def test_jornada_regular_8_horas(self):

        dia = self.dia(
            1
        )

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

        dia.saida_2 = time(
            17,
            0,
        )

        dia.save()

        resultado = (
            apurar_dia_folha_ponto(
                dia
            )
        )

        self.assertEqual(
            resultado["status"],
            "regular",
        )

        self.assertEqual(
            dia.horas_trabalhadas,
            Decimal("8.00"),
        )

        self.assertEqual(
            dia.horas_extras,
            Decimal("0.00"),
        )

        self.assertEqual(
            dia.horas_faltas_atrasos,
            Decimal("0.00"),
        )

    def test_hora_extra(self):

        dia = self.dia(
            1
        )

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

        dia.saida_2 = time(
            18,
            0,
        )

        dia.save()

        resultado = (
            apurar_dia_folha_ponto(
                dia
            )
        )

        self.assertEqual(
            resultado["status"],
            "com_extra",
        )

        self.assertEqual(
            dia.horas_trabalhadas,
            Decimal("8.00"),
        )

        self.assertEqual(
            dia.horas_extras,
            Decimal("1.00"),
        )

        self.assertEqual(
            dia.saldo_banco_candidato,
            Decimal("1.00"),
        )

    def test_jornada_incompleta(self):

        dia = self.dia(
            1
        )

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

        dia.saida_2 = time(
            16,
            0,
        )

        dia.save()

        resultado = (
            apurar_dia_folha_ponto(
                dia
            )
        )

        self.assertEqual(
            resultado["status"],
            "jornada_incompleta",
        )

        self.assertEqual(
            dia.horas_trabalhadas,
            Decimal("7.00"),
        )

        self.assertEqual(
            dia.horas_faltas_atrasos,
            Decimal("1.00"),
        )

        self.assertEqual(
            dia.saldo_banco_candidato,
            Decimal("-1.00"),
        )

    def test_sem_marcacao_nao_vira_falta(
        self
    ):

        dia = self.dia(
            1
        )

        resultado = (
            apurar_dia_folha_ponto(
                dia
            )
        )

        self.assertEqual(
            resultado["status"],
            "sem_marcacao",
        )

        self.assertEqual(
            dia.horas_faltas_atrasos,
            Decimal("0.00"),
        )

    def test_marcacao_incompleta_e_erro(self):

        dia = self.dia(
            1
        )

        dia.entrada_1 = time(
            8,
            0,
        )

        dia.save()

        with self.assertRaises(
            ValidationError
        ):
            apurar_dia_folha_ponto(
                dia
            )

    def test_descanso_trabalhado_gera_saldo(
        self
    ):

        dia = self.dia(
            6
        )

        self.assertEqual(
            dia.tipo_dia,
            "descanso",
        )

        dia.entrada_1 = time(
            8,
            0,
        )

        dia.saida_1 = time(
            12,
            0,
        )

        dia.save()

        resultado = (
            apurar_dia_folha_ponto(
                dia
            )
        )

        self.assertEqual(
            resultado["status"],
            "descanso_trabalhado",
        )

        self.assertEqual(
            dia.horas_extras,
            Decimal("4.00"),
        )

        self.assertEqual(
            dia.saldo_banco_candidato,
            Decimal("4.00"),
        )

    def test_ferias_nao_geram_falta(self):

        periodo = PeriodoAquisitivoFerias.objects.create(
            funcionario=self.funcionario,
            data_inicio=date(
                2025,
                1,
                1,
            ),
            data_fim=date(
                2025,
                12,
                31,
            ),
        )

        FeriasFuncionario.objects.create(
            funcionario=self.funcionario,
            periodo_aquisitivo=periodo,
            data_inicio=date(
                2026,
                10,
                1,
            ),
            data_fim=date(
                2026,
                10,
                5,
            ),
            dias_gozo=Decimal(
                "5.00"
            ),
            status="confirmada",
        )

        gerar_calendario_folha_ponto(
            self.folha
        )

        dia = self.dia(
            1
        )

        resultado = (
            apurar_dia_folha_ponto(
                dia
            )
        )

        self.assertEqual(
            resultado["status"],
            "ferias",
        )

        self.assertEqual(
            dia.horas_faltas_atrasos,
            Decimal("0.00"),
        )

    def test_afastamento_abonado_nao_gera_falta(
        self
    ):

        tipo = TipoAfastamento.objects.create(
            codigo="atestado",
            nome="Atestado",
            data_inicio_vigencia=date(
                2026,
                1,
                1,
            ),
            abona_ponto=True,
            remunerado=True,
            exige_documento=True,
            documento_sensivel=True,
        )

        AfastamentoFuncionario.objects.create(
            funcionario=self.funcionario,
            tipo=tipo,
            data_inicio=date(
                2026,
                10,
                1,
            ),
            data_fim=date(
                2026,
                10,
                1,
            ),
            status="confirmado",
        )

        gerar_calendario_folha_ponto(
            self.folha
        )

        dia = self.dia(
            1
        )

        resultado = (
            apurar_dia_folha_ponto(
                dia
            )
        )

        self.assertEqual(
            resultado["status"],
            "afastamento_abonado",
        )

        self.assertEqual(
            dia.horas_faltas_atrasos,
            Decimal("0.00"),
        )

    def test_afastamento_nao_abonado_nao_e_falta_injustificada(
        self
    ):

        tipo = TipoAfastamento.objects.create(
            codigo="licenca-nao-remunerada",
            nome="Licenca nao remunerada",
            data_inicio_vigencia=date(
                2026,
                1,
                1,
            ),
            abona_ponto=False,
            remunerado=False,
        )

        AfastamentoFuncionario.objects.create(
            funcionario=self.funcionario,
            tipo=tipo,
            data_inicio=date(
                2026,
                10,
                1,
            ),
            data_fim=date(
                2026,
                10,
                1,
            ),
            status="confirmado",
        )

        gerar_calendario_folha_ponto(
            self.folha
        )

        dia = self.dia(
            1
        )

        resultado = (
            apurar_dia_folha_ponto(
                dia
            )
        )

        self.assertEqual(
            resultado["status"],
            "afastamento_nao_abonado",
        )

        self.assertEqual(
            dia.horas_faltas_atrasos,
            Decimal("0.00"),
        )
