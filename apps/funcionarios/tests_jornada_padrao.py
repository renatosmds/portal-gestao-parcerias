from datetime import date, time
from decimal import Decimal

from django.test import TestCase

from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    EscalaFuncionario,
    EscalaTrabalho,
    FolhaPonto,
    Funcionario,
    JornadaEscala,
)
from apps.funcionarios.services import (
    gerar_calendario_folha_ponto,
    preencher_jornada_padrao_folha,
)


class JornadaPadraoTests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="Empresa Jornada Padrao",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Funcionario Jornada Padrao",
            usuario="jornada-padrao",
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
        )

        self.escala = EscalaTrabalho.objects.create(
            empresa=self.empresa,
            nome="5x2 40h",
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

            trabalha = (
                posicao <= 5
            )

            JornadaEscala.objects.create(
                escala=self.escala,
                posicao_ciclo=posicao,
                trabalha=trabalha,
                horas_previstas=(
                    Decimal("8.00")
                    if trabalha
                    else Decimal("0.00")
                ),
                hora_entrada=(
                    time(8, 0)
                    if trabalha
                    else None
                ),
                hora_saida=(
                    time(17, 0)
                    if trabalha
                    else None
                ),
                intervalo_minutos=(
                    60
                    if trabalha
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
                9,
                28,
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

    def test_preenche_08_12_13_17(self):

        resultado = (
            preencher_jornada_padrao_folha(
                self.folha
            )
        )

        dia = self.folha.dias.get(
            data=date(
                2026,
                10,
                1,
            )
        )

        self.assertEqual(
            dia.entrada_1,
            time(8, 0),
        )

        self.assertEqual(
            dia.saida_1,
            time(12, 0),
        )

        self.assertEqual(
            dia.entrada_2,
            time(13, 0),
        )

        self.assertEqual(
            dia.saida_2,
            time(17, 0),
        )

        self.assertGreater(
            resultado[
                "preenchidos"
            ],
            0,
        )

    def test_descanso_permanece_vazio(self):

        preencher_jornada_padrao_folha(
            self.folha
        )

        dia = self.folha.dias.get(
            data=date(
                2026,
                10,
                3,
            )
        )

        self.assertEqual(
            dia.tipo_dia,
            "descanso",
        )

        self.assertIsNone(
            dia.entrada_1
        )

        self.assertIsNone(
            dia.saida_1
        )

        self.assertIsNone(
            dia.entrada_2
        )

        self.assertIsNone(
            dia.saida_2
        )

    def test_nao_sobrescreve_marcacao_manual(self):

        dia = self.folha.dias.get(
            data=date(
                2026,
                10,
                1,
            )
        )

        dia.entrada_1 = time(
            7,
            55,
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
            10,
        )

        dia.save()

        resultado = (
            preencher_jornada_padrao_folha(
                self.folha
            )
        )

        dia.refresh_from_db()

        self.assertEqual(
            dia.entrada_1,
            time(7, 55),
        )

        self.assertEqual(
            dia.saida_2,
            time(17, 10),
        )

        self.assertGreaterEqual(
            resultado[
                "preservados"
            ],
            1,
        )
