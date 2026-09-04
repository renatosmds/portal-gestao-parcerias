from datetime import date
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import CompetenciaPrestacao, Prestacao


class Sprint4619CompetenciaPrestacaoTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Teste Sprint 46.19",
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            tipo="cnpj",
            numtermo="TESTE-001/2026",
        )

        self.competencia = CompetenciaPrestacao.objects.create(
            prestacao=self.prestacao,
            ano=2026,
            mes=1,
            data_inicial=date(2026, 1, 1),
            data_final=date(2026, 1, 31),
            saldo_inicial=Decimal("1000.00"),
            saldo_final=Decimal("500.00"),
        )

    def test_cria_competencia_mensal(self):
        self.assertEqual(self.competencia.ano, 2026)
        self.assertEqual(self.competencia.mes, 1)
        self.assertEqual(
            str(self.competencia),
            f"01/2026 - {self.prestacao}",
        )

    def test_mes_invalido_e_bloqueado(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CompetenciaPrestacao.objects.create(
                    prestacao=self.prestacao,
                    ano=2026,
                    mes=13,
                    data_inicial=date(2026, 1, 1),
                    data_final=date(2026, 1, 31),
                )

    def test_competencia_duplicada_e_bloqueada(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CompetenciaPrestacao.objects.create(
                    prestacao=self.prestacao,
                    ano=2026,
                    mes=1,
                    data_inicial=date(2026, 1, 1),
                    data_final=date(2026, 1, 31),
                )

    def test_lancamento_pode_ser_vinculado_a_competencia(self):
        lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            prestacao=self.prestacao,
            competencia=self.competencia,
            numero_lancamento="TESTE-46-19",
            data_documento=date(2026, 1, 15),
            descricao="Despesa de teste",
            valor_documento=Decimal("150.00"),
        )

        self.assertEqual(
            lancamento.competencia_id,
            self.competencia.id,
        )

        self.assertEqual(
            self.competencia.lancamentos.count(),
            1,
        )

        self.assertEqual(
            self.competencia.lancamentos.first(),
            lancamento,
        )

    def test_lancamento_sem_competencia_continua_valido(self):
        lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            prestacao=self.prestacao,
            numero_lancamento="TESTE-SEM-COMP",
            data_documento=date(2026, 1, 20),
            descricao="Despesa sem competencia",
            valor_documento=Decimal("200.00"),
        )

        self.assertIsNone(lancamento.competencia)
