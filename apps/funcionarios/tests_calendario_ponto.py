from datetime import date
from decimal import Decimal

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
    classificar_dia_folha_ponto,
    gerar_calendario_folha_ponto,
)


class CalendarioPontoTests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Calendario Ponto",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Calendario",
            usuario="calendario",
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
            nome="5x2 teste",
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

    def test_classifica_trabalho(self):

        resultado = (
            classificar_dia_folha_ponto(
                self.funcionario,
                date(
                    2026,
                    10,
                    1,
                ),
            )
        )

        self.assertEqual(
            resultado["tipo_dia"],
            "trabalho",
        )

        self.assertEqual(
            resultado["horas_previstas"],
            Decimal("8.00"),
        )

    def test_classifica_descanso(self):

        resultado = (
            classificar_dia_folha_ponto(
                self.funcionario,
                date(
                    2026,
                    10,
                    6,
                ),
            )
        )

        self.assertEqual(
            resultado["tipo_dia"],
            "descanso",
        )

    def test_ferias_tem_prioridade_sobre_trabalho(
        self
    ):

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

        resultado = (
            classificar_dia_folha_ponto(
                self.funcionario,
                date(
                    2026,
                    10,
                    1,
                ),
            )
        )

        self.assertEqual(
            resultado["tipo_dia"],
            "ferias",
        )

        self.assertEqual(
            resultado["horas_abonadas"],
            Decimal("8.00"),
        )

    def test_afastamento_abonado_nao_vira_falta(
        self
    ):

        tipo = TipoAfastamento.objects.create(
            codigo="licenca-remunerada",
            nome="Licenca remunerada",
            data_inicio_vigencia=date(
                2026,
                1,
                1,
            ),
            abona_ponto=True,
            remunerado=True,
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
                2,
            ),
            status="confirmado",
        )

        resultado = (
            classificar_dia_folha_ponto(
                self.funcionario,
                date(
                    2026,
                    10,
                    1,
                ),
            )
        )

        self.assertEqual(
            resultado["tipo_dia"],
            "afastamento_abonado",
        )

        self.assertEqual(
            resultado["horas_abonadas"],
            Decimal("8.00"),
        )

    def test_afastamento_nao_abonado_e_identificado(
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
                2,
            ),
            status="confirmado",
        )

        resultado = (
            classificar_dia_folha_ponto(
                self.funcionario,
                date(
                    2026,
                    10,
                    1,
                ),
            )
        )

        self.assertEqual(
            resultado["tipo_dia"],
            "afastamento_nao_abonado",
        )

        self.assertEqual(
            resultado["horas_abonadas"],
            Decimal("0.00"),
        )

    def test_fora_do_vinculo(self):

        resultado = (
            classificar_dia_folha_ponto(
                self.funcionario,
                date(
                    2026,
                    9,
                    30,
                ),
            )
        )

        self.assertEqual(
            resultado["tipo_dia"],
            "fora_vinculo",
        )

    def test_gera_todos_os_dias_da_competencia(
        self
    ):

        folha = FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(
                2026,
                10,
                1,
            ),
        )

        resultado = gerar_calendario_folha_ponto(
            folha
        )

        self.assertEqual(
            resultado["criados"],
            31,
        )

        self.assertEqual(
            folha.dias.count(),
            31,
        )

    def test_regenerar_nao_duplica_dias(self):

        folha = FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(
                2026,
                10,
                1,
            ),
        )

        gerar_calendario_folha_ponto(
            folha
        )

        resultado = gerar_calendario_folha_ponto(
            folha
        )

        self.assertEqual(
            folha.dias.count(),
            31,
        )

        self.assertEqual(
            resultado["criados"],
            0,
        )

        self.assertEqual(
            resultado["atualizados"],
            31,
        )

    def test_regeneracao_preserva_horas_trabalhadas(
        self
    ):

        folha = FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(
                2026,
                10,
                1,
            ),
        )

        gerar_calendario_folha_ponto(
            folha
        )

        dia = folha.dias.get(
            data=date(
                2026,
                10,
                1,
            )
        )

        dia.horas_trabalhadas = Decimal(
            "8.00"
        )

        dia.save(
            update_fields=[
                "horas_trabalhadas"
            ]
        )

        gerar_calendario_folha_ponto(
            folha
        )

        dia.refresh_from_db()

        self.assertEqual(
            dia.horas_trabalhadas,
            Decimal("8.00"),
        )
