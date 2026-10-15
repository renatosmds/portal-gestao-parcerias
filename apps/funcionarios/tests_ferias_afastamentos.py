from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    AfastamentoFuncionario,
    FeriasFuncionario,
    Funcionario,
    PeriodoAquisitivoFerias,
    TipoAfastamento,
)


class FeriasAfastamentosTests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Ferias Teste",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Ferias",
            usuario="ferias",
            cpf="52998224725",
            empresa=self.empresa,
            data_admissao=date(
                2025,
                1,
                1,
            ),
        )

        self.tipo = TipoAfastamento.objects.create(
            codigo="licenca-remunerada",
            nome="Licenca remunerada",
            data_inicio_vigencia=date(
                2025,
                1,
                1,
            ),
            abona_ponto=True,
            remunerado=True,
        )

    def test_cria_tipo_afastamento(self):

        self.assertTrue(
            self.tipo.abona_ponto
        )

        self.assertTrue(
            self.tipo.remunerado
        )

    def test_afastamento_calcula_dias(self):

        afastamento = AfastamentoFuncionario(
            funcionario=self.funcionario,
            tipo=self.tipo,
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
            status="confirmado",
        )

        afastamento.full_clean()
        afastamento.save()

        self.assertEqual(
            afastamento.quantidade_dias,
            5,
        )

    def test_afastamento_fim_antes_inicio_invalido(
        self
    ):

        afastamento = AfastamentoFuncionario(
            funcionario=self.funcionario,
            tipo=self.tipo,
            data_inicio=date(
                2026,
                10,
                10,
            ),
            data_fim=date(
                2026,
                10,
                5,
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            afastamento.full_clean()

    def test_afastamentos_sobrepostos_invalidos(
        self
    ):

        AfastamentoFuncionario.objects.create(
            funcionario=self.funcionario,
            tipo=self.tipo,
            data_inicio=date(
                2026,
                10,
                1,
            ),
            data_fim=date(
                2026,
                10,
                10,
            ),
            status="confirmado",
        )

        segundo = AfastamentoFuncionario(
            funcionario=self.funcionario,
            tipo=self.tipo,
            data_inicio=date(
                2026,
                10,
                5,
            ),
            data_fim=date(
                2026,
                10,
                15,
            ),
            status="confirmado",
        )

        with self.assertRaises(
            ValidationError
        ):
            segundo.full_clean()

    def test_periodo_aquisitivo_saldo(self):

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
            dias_direito=Decimal(
                "30.00"
            ),
            dias_gozados=Decimal(
                "10.00"
            ),
            dias_abono=Decimal(
                "0.00"
            ),
        )

        self.assertEqual(
            periodo.saldo_dias,
            Decimal("20.00"),
        )

    def test_periodo_aquisitivo_nao_excede_direito(
        self
    ):

        periodo = PeriodoAquisitivoFerias(
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
            dias_direito=Decimal(
                "30.00"
            ),
            dias_gozados=Decimal(
                "25.00"
            ),
            dias_abono=Decimal(
                "10.00"
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            periodo.full_clean()

    def test_ferias_validas(self):

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

        ferias = FeriasFuncionario(
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
                15,
            ),
            dias_gozo=Decimal(
                "15.00"
            ),
            status="confirmada",
        )

        ferias.full_clean()
        ferias.save()

        self.assertIsNotNone(
            ferias.pk
        )

    def test_ferias_dias_nao_correspondentes_invalidos(
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

        ferias = FeriasFuncionario(
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
                15,
            ),
            dias_gozo=Decimal(
                "10.00"
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            ferias.full_clean()

    def test_ferias_periodo_de_outro_funcionario_invalido(
        self
    ):

        outro = Funcionario.objects.create(
            nome="Outro Colaborador",
            usuario="outro",
            cpf="16899535009",
            empresa=self.empresa,
            data_admissao=date(
                2025,
                1,
                1,
            ),
        )

        periodo = PeriodoAquisitivoFerias.objects.create(
            funcionario=outro,
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

        ferias = FeriasFuncionario(
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
                15,
            ),
            dias_gozo=Decimal(
                "15.00"
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            ferias.full_clean()

    def test_ferias_sobrepostas_invalidas(self):

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
                10,
            ),
            dias_gozo=Decimal(
                "10.00"
            ),
            status="confirmada",
        )

        segunda = FeriasFuncionario(
            funcionario=self.funcionario,
            periodo_aquisitivo=periodo,
            data_inicio=date(
                2026,
                10,
                8,
            ),
            data_fim=date(
                2026,
                10,
                15,
            ),
            dias_gozo=Decimal(
                "8.00"
            ),
            status="confirmada",
        )

        with self.assertRaises(
            ValidationError
        ):
            segunda.full_clean()
