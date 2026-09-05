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


    def _criar_lancamento(
        self,
        numero,
        valor,
        situacao=Lancamento.Situacao.NAO_ANALISADO,
        valor_glosa=Decimal("0.00"),
        descricao="Despesa de teste",
    ):
        return Lancamento.objects.create(
            empresa=self.empresa,
            prestacao=self.prestacao,
            competencia=self.competencia,
            numero_lancamento=numero,
            data_documento=date(2026, 1, 15),
            descricao=descricao,
            valor_documento=Decimal(valor),
            valor_glosa=valor_glosa,
            situacao=situacao,
        )

    def test_lista_filtra_por_competencia(self):
        self._criar_lancamento(
            "COMP-01",
            "100.00",
        )

        outra_competencia = CompetenciaPrestacao.objects.create(
            prestacao=self.prestacao,
            ano=2026,
            mes=2,
            data_inicial=date(2026, 2, 1),
            data_final=date(2026, 2, 28),
        )

        Lancamento.objects.create(
            empresa=self.empresa,
            prestacao=self.prestacao,
            competencia=outra_competencia,
            numero_lancamento="COMP-02",
            data_documento=date(2026, 2, 10),
            descricao="Outra competencia",
            valor_documento=Decimal("200.00"),
        )

        self.client.force_login(
            __import__(
                "django.contrib.auth"
            ).contrib.auth.get_user_model().objects.create_superuser(
                username="admin4619",
                email="admin4619@example.com",
                password="teste123",
            )
        )

        resposta = self.client.get(
            "/lancamentos/",
            {"competencia": self.competencia.pk},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "COMP-01")
        self.assertNotContains(resposta, "COMP-02")

    def test_painel_mensal_exibe_competencia(self):
        self.client.force_login(
            __import__(
                "django.contrib.auth"
            ).contrib.auth.get_user_model().objects.create_superuser(
                username="admin4619b",
                email="admin4619b@example.com",
                password="teste123",
            )
        )

        resposta = self.client.get(
            "/lancamentos/",
            {"competencia": self.competencia.pk},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "COMPET?NCIA SELECIONADA")
        self.assertContains(resposta, "01/2026")

    def test_resumo_consolidado_da_competencia(self):
        self._criar_lancamento(
            "REG-01",
            "100.00",
            Lancamento.Situacao.REGULAR,
        )
        self._criar_lancamento(
            "RES-01",
            "200.00",
            Lancamento.Situacao.RESSALVA,
        )
        self._criar_lancamento(
            "GLO-01",
            "300.00",
            Lancamento.Situacao.GLOSADO,
            Decimal("50.00"),
        )
        self._criar_lancamento(
            "NAO-01",
            "400.00",
            Lancamento.Situacao.NAO_ANALISADO,
        )

        self.client.force_login(
            __import__(
                "django.contrib.auth"
            ).contrib.auth.get_user_model().objects.create_superuser(
                username="admin4619c",
                email="admin4619c@example.com",
                password="teste123",
            )
        )

        resposta = self.client.get(
            "/lancamentos/",
            {"competencia": self.competencia.pk},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.context["competencia_qtd_lancamentos"],
            4,
        )
        self.assertEqual(
            resposta.context["competencia_regulares"],
            1,
        )
        self.assertEqual(
            resposta.context["competencia_ressalvas"],
            1,
        )
        self.assertEqual(
            resposta.context["competencia_glosados"],
            1,
        )
        self.assertEqual(
            resposta.context["competencia_nao_analisados"],
            1,
        )
        self.assertEqual(
            resposta.context["competencia_total_documentos"],
            Decimal("1000.00"),
        )
        self.assertEqual(
            resposta.context["competencia_total_glosas"],
            Decimal("50.00"),
        )
        self.assertEqual(
            resposta.context["competencia_total_aprovado"],
            Decimal("950.00"),
        )

    def test_resumo_nao_muda_com_filtro_de_situacao(self):
        self._criar_lancamento(
            "REG-FILTRO",
            "100.00",
            Lancamento.Situacao.REGULAR,
        )
        self._criar_lancamento(
            "GLO-FILTRO",
            "300.00",
            Lancamento.Situacao.GLOSADO,
            Decimal("50.00"),
        )

        self.client.force_login(
            __import__(
                "django.contrib.auth"
            ).contrib.auth.get_user_model().objects.create_superuser(
                username="admin4619d",
                email="admin4619d@example.com",
                password="teste123",
            )
        )

        resposta = self.client.get(
            "/lancamentos/",
            {
                "competencia": self.competencia.pk,
                "situacao": Lancamento.Situacao.REGULAR,
            },
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertEqual(
            len(resposta.context["object_list"]),
            1,
        )

        self.assertEqual(
            resposta.context["competencia_qtd_lancamentos"],
            2,
        )
        self.assertEqual(
            resposta.context["competencia_total_documentos"],
            Decimal("400.00"),
        )
        self.assertEqual(
            resposta.context["competencia_total_glosas"],
            Decimal("50.00"),
        )
