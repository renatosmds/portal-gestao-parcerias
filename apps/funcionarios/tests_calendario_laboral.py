from datetime import date, time
from decimal import Decimal

from django.test import TestCase

from apps.empresas.models import Empresa

from .models import (
    CalendarioLaboral,
    EscalaFuncionario,
    EscalaTrabalho,
    Feriado,
    FolhaPonto,
    Funcionario,
    JornadaEscala,
)
from .services import (
    apurar_dia_folha_ponto,
    classificar_dia_folha_ponto,
    gerar_calendario_folha_ponto,
)
from .services_calendario import (
    calendario_laboral_vigente,
    evento_calendario_aplicavel_data,
)


class CalendarioLaboralTests(TestCase):

    def setUp(self):

        self.empresa = Empresa.objects.create(
            nome="OSC Calendario Laboral",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Colaborador Calendario Laboral",
            usuario="calendario-laboral",
            cpf="39053344705",
            empresa=self.empresa,
            data_admissao=date(
                2026,
                1,
                1,
            ),
        )

        self.calendario = (
            CalendarioLaboral.objects.create(
                empresa=self.empresa,
                nome="Contagem MG",
                uf="MG",
                municipio="Contagem",
                vigencia_inicio=date(
                    2026,
                    1,
                    1,
                ),
            )
        )

        self.escala = (
            EscalaTrabalho.objects.create(
                empresa=self.empresa,
                nome="5x2 Calendario",
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
                1,
                1,
            ),
            data_referencia=date(
                2026,
                1,
                5,
            ),
        )

    def test_resolve_calendario_empresa(self):

        encontrado = (
            calendario_laboral_vigente(
                self.funcionario,
                date(
                    2026,
                    10,
                    1,
                ),
            )
        )

        self.assertEqual(
            encontrado,
            self.calendario,
        )

    def test_feriado_nacional_aplica(self):

        feriado = Feriado.objects.create(
            nome="Feriado Nacional Teste",
            data=date(
                2026,
                10,
                1,
            ),
            natureza="feriado",
            abrangencia="nacional",
        )

        evento = (
            evento_calendario_aplicavel_data(
                self.funcionario,
                feriado.data,
            )
        )

        self.assertEqual(
            evento["feriado"],
            feriado,
        )

        self.assertEqual(
            evento["tipo"],
            "feriado",
        )

    def test_feriado_estadual_aplica_por_uf(self):

        feriado = Feriado.objects.create(
            nome="Feriado Estadual Teste",
            data=date(
                2026,
                10,
                2,
            ),
            natureza="feriado",
            abrangencia="estadual",
            uf="MG",
        )

        evento = (
            evento_calendario_aplicavel_data(
                self.funcionario,
                feriado.data,
            )
        )

        self.assertEqual(
            evento["feriado"],
            feriado,
        )

    def test_feriado_municipal_aplica_por_localidade(
        self,
    ):

        feriado = Feriado.objects.create(
            nome="Feriado Municipal Teste",
            data=date(
                2026,
                10,
                5,
            ),
            natureza="feriado",
            abrangencia="municipal",
            uf="MG",
            municipio="Contagem",
        )

        evento = (
            evento_calendario_aplicavel_data(
                self.funcionario,
                feriado.data,
            )
        )

        self.assertEqual(
            evento["feriado"],
            feriado,
        )

    def test_feriado_municipal_outro_municipio_nao_aplica(
        self,
    ):

        Feriado.objects.create(
            nome="Municipal Outra Cidade",
            data=date(
                2026,
                10,
                6,
            ),
            natureza="feriado",
            abrangencia="municipal",
            uf="MG",
            municipio="Belo Horizonte",
        )

        evento = (
            evento_calendario_aplicavel_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    6,
                ),
            )
        )

        self.assertIsNone(
            evento
        )

    def test_ponto_facultativo_nao_e_feriado_automatico(
        self,
    ):

        Feriado.objects.create(
            nome="Ponto Facultativo Teste",
            data=date(
                2026,
                10,
                7,
            ),
            natureza="ponto_facultativo",
            abrangencia="nacional",
        )

        evento = (
            evento_calendario_aplicavel_data(
                self.funcionario,
                date(
                    2026,
                    10,
                    7,
                ),
            )
        )

        self.assertIsNone(
            evento
        )

    def test_ponto_facultativo_pode_ser_adotado(
        self,
    ):

        self.calendario.considera_ponto_facultativo = True
        self.calendario.save(
            update_fields=[
                "considera_ponto_facultativo",
            ]
        )

        feriado = Feriado.objects.create(
            nome="Ponto Facultativo Adotado",
            data=date(
                2026,
                10,
                8,
            ),
            natureza="ponto_facultativo",
            abrangencia="nacional",
        )

        evento = (
            evento_calendario_aplicavel_data(
                self.funcionario,
                feriado.data,
            )
        )

        self.assertEqual(
            evento["tipo"],
            "ponto_facultativo",
        )

    def test_feriado_tem_prioridade_sobre_escala(
        self,
    ):

        feriado = Feriado.objects.create(
            nome="Feriado Prioridade",
            data=date(
                2026,
                10,
                1,
            ),
            natureza="feriado",
            abrangencia="nacional",
        )

        resultado = (
            classificar_dia_folha_ponto(
                self.funcionario,
                feriado.data,
            )
        )

        self.assertEqual(
            resultado["tipo_dia"],
            "feriado",
        )

        self.assertEqual(
            resultado["feriado"],
            feriado,
        )

    def test_trabalho_feriado_fica_separado_da_hora_extra(
        self,
    ):

        Feriado.objects.create(
            nome="Feriado Trabalho Teste",
            data=date(
                2026,
                10,
                1,
            ),
            natureza="feriado",
            abrangencia="nacional",
        )

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

        self.assertEqual(
            dia.tipo_dia,
            "feriado",
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

        dia.refresh_from_db()

        self.assertEqual(
            resultado["status"],
            "feriado_trabalhado",
        )

        self.assertEqual(
            dia.horas_feriado,
            Decimal("8.00"),
        )

        self.assertEqual(
            dia.horas_extras,
            Decimal("0.00"),
        )

        self.assertEqual(
            dia.saldo_banco_candidato,
            Decimal("0.00"),
        )
