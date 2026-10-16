from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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
)


class InterfaceEscalasTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_superuser(
            username="teste-escalas",
            email="escalas@pgp.local",
            password="Senha123!",
        )

        self.client.force_login(
            self.user
        )

        self.empresa = Empresa.objects.create(
            nome="Empresa Escalas",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Funcionario Escala",
            usuario="func-escala",
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

    def test_tela_lista_escalas(self):

        response = self.client.get(
            reverse(
                "escalas_list"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Escalas e Jornadas",
        )

    def test_tela_vinculos(self):

        response = self.client.get(
            reverse(
                "vinculos_escala_list"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Vínculos de Escala",
        )

    def test_vinculo_regenera_folha_aberta(self):

        escala = EscalaTrabalho.objects.create(
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

            JornadaEscala.objects.create(
                escala=escala,
                posicao_ciclo=posicao,
                trabalha=(
                    posicao <= 5
                ),
                horas_previstas=(
                    Decimal("8.00")
                    if posicao <= 5
                    else Decimal("0.00")
                ),
                hora_entrada=(
                    None
                    if posicao > 5
                    else __import__(
                        "datetime"
                    ).time(
                        8,
                        0,
                    )
                ),
                hora_saida=(
                    None
                    if posicao > 5
                    else __import__(
                        "datetime"
                    ).time(
                        17,
                        0,
                    )
                ),
                intervalo_minutos=(
                    0
                    if posicao > 5
                    else 60
                ),
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

        self.assertTrue(
            folha.dias.filter(
                tipo_dia="sem_configuracao"
            ).exists()
        )

        response = self.client.post(
            reverse(
                "vinculo_escala_create"
            ),
            {
                "funcionario": (
                    self.funcionario.pk
                ),
                "escala": escala.pk,
                "data_inicio": (
                    "2026-10-01"
                ),
                "data_fim": "",
                "data_referencia": (
                    "2026-10-01"
                ),
                "observacoes": "",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            EscalaFuncionario.objects.count(),
            1,
        )

        folha.refresh_from_db()

        self.assertFalse(
            folha.dias.filter(
                tipo_dia="sem_configuracao"
            ).exists()
        )

        self.assertTrue(
            folha.dias.filter(
                tipo_dia="trabalho"
            ).exists()
        )

        self.assertTrue(
            folha.dias.filter(
                tipo_dia="descanso"
            ).exists()
        )
