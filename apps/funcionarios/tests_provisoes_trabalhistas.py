from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.empresas.models import Empresa

from .models import (
    Funcionario,
    ParametroTrabalhista,
    ProvisaoTrabalhista,
)
from .services_provisoes import (
    calcular_por_percentual,
    criar_ou_atualizar_provisao,
    parametro_trabalhista_vigente,
)


class ProvisoesTrabalhistasTests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Provisoes",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Provisoes",
            usuario="colaborador-provisoes",
            cpf="39053344705",
            empresa=self.empresa,
            data_admissao=date(
                2026,
                1,
                1,
            ),
            salarioBase=Decimal(
                "3000.00"
            ),
        )

    def test_parametro_vigente_por_data(self):

        antigo = (
            ParametroTrabalhista.objects.create(
                codigo="fgts",
                nome="FGTS antigo",
                percentual=Decimal(
                    "7.000000"
                ),
                vigencia_inicio=date(
                    2025,
                    1,
                    1,
                ),
                vigencia_fim=date(
                    2025,
                    12,
                    31,
                ),
            )
        )

        atual = (
            ParametroTrabalhista.objects.create(
                codigo="fgts",
                nome="FGTS atual",
                percentual=Decimal(
                    "8.000000"
                ),
                vigencia_inicio=date(
                    2026,
                    1,
                    1,
                ),
            )
        )

        encontrado = (
            parametro_trabalhista_vigente(
                "fgts",
                date(
                    2026,
                    10,
                    1,
                ),
            )
        )

        self.assertEqual(
            encontrado,
            atual,
        )

        self.assertNotEqual(
            encontrado,
            antigo,
        )

    def test_calculo_percentual(self):

        valor = calcular_por_percentual(
            Decimal("3000.00"),
            Decimal("8.00"),
        )

        self.assertEqual(
            valor,
            Decimal("240.00"),
        )

    def test_provisao_competencia_primeiro_dia(self):

        obj = ProvisaoTrabalhista(
            funcionario=self.funcionario,
            competencia=date(
                2026,
                10,
                15,
            ),
            tipo="ferias",
            base_calculo=Decimal(
                "3000.00"
            ),
            valor=Decimal(
                "250.00"
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            obj.full_clean()

    def test_provisao_automatica_idempotente(self):

        competencia = date(
            2026,
            10,
            1,
        )

        primeira, criada1 = (
            criar_ou_atualizar_provisao(
                funcionario=self.funcionario,
                competencia=competencia,
                tipo="ferias",
                base_calculo=Decimal(
                    "3000.00"
                ),
                valor=Decimal(
                    "250.00"
                ),
                quantidade_avos=Decimal(
                    "1.00"
                ),
            )
        )

        segunda, criada2 = (
            criar_ou_atualizar_provisao(
                funcionario=self.funcionario,
                competencia=competencia,
                tipo="ferias",
                base_calculo=Decimal(
                    "3000.00"
                ),
                valor=Decimal(
                    "260.00"
                ),
                quantidade_avos=Decimal(
                    "1.00"
                ),
            )
        )

        self.assertTrue(
            criada1
        )

        self.assertFalse(
            criada2
        )

        self.assertEqual(
            primeira.pk,
            segunda.pk,
        )

        segunda.refresh_from_db()

        self.assertEqual(
            segunda.valor,
            Decimal("260.00"),
        )

        self.assertEqual(
            ProvisaoTrabalhista.objects.count(),
            1,
        )
