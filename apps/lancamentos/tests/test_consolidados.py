from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import CompetenciaPrestacao, Prestacao
from apps.termos.models import Termos


class ConsolidadosHierarquiaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            username="admin_consolidados",
            email="admin@example.com",
            password="senha-teste-123",
        )

        cls.empresa = Empresa.objects.create(
            nome="Empresa Consolidados"
        )

        cls.termo = Termos.objects.create(
            empresa=cls.empresa,
            termo="Termo de Colaboração",
            numtermo="CONS-001/2026",
        )

        cls.prestacao_1 = Prestacao.objects.create(
            empresa=cls.empresa,
            termo=cls.termo,
            tipo="cnpj",
            numtermo="CONS-001/2026",
        )

        cls.prestacao_2 = Prestacao.objects.create(
            empresa=cls.empresa,
            termo=cls.termo,
            tipo="cnpj",
            numtermo="CONS-001/2026-P2",
        )

        cls.competencia_1 = CompetenciaPrestacao.objects.create(
            prestacao=cls.prestacao_1,
            ano=2026,
            mes=1,
            data_inicial=date(2026, 1, 1),
            data_final=date(2026, 1, 31),
        )

        cls.competencia_2 = CompetenciaPrestacao.objects.create(
            prestacao=cls.prestacao_1,
            ano=2026,
            mes=2,
            data_inicial=date(2026, 2, 1),
            data_final=date(2026, 2, 28),
        )

        cls.competencia_3 = CompetenciaPrestacao.objects.create(
            prestacao=cls.prestacao_2,
            ano=2026,
            mes=3,
            data_inicial=date(2026, 3, 1),
            data_final=date(2026, 3, 31),
        )

        cls._criar_lancamento(
            "C001",
            cls.prestacao_1,
            cls.competencia_1,
            "1000.00",
            "0.00",
            Lancamento.Situacao.REGULAR,
        )

        cls._criar_lancamento(
            "C002",
            cls.prestacao_1,
            cls.competencia_1,
            "500.00",
            "0.00",
            Lancamento.Situacao.RESSALVA,
        )

        cls._criar_lancamento(
            "C003",
            cls.prestacao_1,
            cls.competencia_2,
            "400.00",
            "100.00",
            Lancamento.Situacao.GLOSADO,
        )

        cls._criar_lancamento(
            "C004",
            cls.prestacao_1,
            cls.competencia_2,
            "300.00",
            "300.00",
            Lancamento.Situacao.REPROVADO,
        )

        cls._criar_lancamento(
            "C005",
            cls.prestacao_1,
            cls.competencia_2,
            "200.00",
            "0.00",
            Lancamento.Situacao.NAO_ANALISADO,
        )

        cls._criar_lancamento(
            "C006",
            cls.prestacao_2,
            cls.competencia_3,
            "700.00",
            "0.00",
            Lancamento.Situacao.REGULAR,
        )

        cls._criar_lancamento(
            "C007",
            cls.prestacao_2,
            cls.competencia_3,
            "600.00",
            "50.00",
            Lancamento.Situacao.GLOSADO,
        )

    @classmethod
    def _criar_lancamento(
        cls,
        numero,
        prestacao,
        competencia,
        valor_documento,
        valor_glosa,
        situacao,
    ):
        return Lancamento.objects.create(
            empresa=cls.empresa,
            termo=cls.termo,
            prestacao=prestacao,
            competencia=competencia,
            numero_lancamento=numero,
            tipo_documento=Lancamento.TipoDocumento.NFE,
            data_documento=date(2026, 1, 15),
            descricao=f"Lançamento {numero}",
            valor_documento=Decimal(valor_documento),
            valor_glosa=Decimal(valor_glosa),
            situacao=situacao,
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def test_consolidado_da_prestacao(self):
        response = self.client.get(
            reverse(
                "detail_prestacao",
                kwargs={"pk": self.prestacao_1.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["total_competencias"],
            2,
        )
        self.assertEqual(
            response.context["total_lancamentos"],
            5,
        )
        self.assertEqual(
            response.context["total_documentos"],
            Decimal("2400.00"),
        )
        self.assertEqual(
            response.context["total_glosado"],
            Decimal("400.00"),
        )
        self.assertEqual(
            response.context["total_aprovado"],
            Decimal("2000.00"),
        )

        self.assertEqual(
            response.context["total_regulares"],
            1,
        )
        self.assertEqual(
            response.context["total_ressalvas"],
            1,
        )
        self.assertEqual(
            response.context["total_glosados"],
            1,
        )
        self.assertEqual(
            response.context["total_reprovados"],
            1,
        )
        self.assertEqual(
            response.context["total_nao_analisados"],
            1,
        )

        self.assertAlmostEqual(
            float(response.context["percentual_aprovado"]),
            83.3333333333,
            places=6,
        )
        self.assertAlmostEqual(
            float(response.context["percentual_glosa"]),
            16.6666666667,
            places=6,
        )
        self.assertAlmostEqual(
            float(response.context["percentual_analisado"]),
            80.0,
            places=6,
        )

    def test_consolidado_do_termo_soma_duas_prestacoes(self):
        response = self.client.get(
            reverse(
                "detail_termo",
                kwargs={"pk": self.termo.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["total_prestacoes_termo"],
            2,
        )
        self.assertEqual(
            response.context["total_competencias_termo"],
            3,
        )
        self.assertEqual(
            response.context["total_lancamentos_termo"],
            7,
        )

        self.assertEqual(
            response.context["total_documentos_termo"],
            Decimal("3700.00"),
        )
        self.assertEqual(
            response.context["total_glosas_termo"],
            Decimal("450.00"),
        )
        self.assertEqual(
            response.context["total_aprovado_termo"],
            Decimal("3250.00"),
        )

        self.assertAlmostEqual(
            float(response.context["percentual_aprovado_termo"]),
            87.8378378378,
            places=6,
        )
        self.assertAlmostEqual(
            float(response.context["percentual_glosa_termo"]),
            12.1621621622,
            places=6,
        )
        self.assertAlmostEqual(
            float(response.context["percentual_analisado_termo"]),
            85.7142857143,
            places=6,
        )

    def test_consolidado_do_termo_conta_situacoes(self):
        response = self.client.get(
            reverse(
                "detail_termo",
                kwargs={"pk": self.termo.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["total_regulares_termo"],
            2,
        )
        self.assertEqual(
            response.context["total_ressalvas_termo"],
            1,
        )
        self.assertEqual(
            response.context["total_glosados_termo"],
            2,
        )
        self.assertEqual(
            response.context["total_reprovados_termo"],
            1,
        )
        self.assertEqual(
            response.context["total_nao_analisados_termo"],
            1,
        )

    def test_lista_filtra_por_prestacao_e_situacao(self):
        response = self.client.get(
            reverse("list_lancamentos"),
            {
                "prestacao": self.prestacao_1.pk,
                "situacao": Lancamento.Situacao.GLOSADO,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["total_lancamentos"],
            1,
        )
        self.assertEqual(
            response.context["prestacao_filtro"],
            str(self.prestacao_1.pk),
        )
        self.assertEqual(
            response.context["situacao_filtro"],
            Lancamento.Situacao.GLOSADO,
        )

    def test_lista_filtra_por_termo_e_situacao(self):
        response = self.client.get(
            reverse("list_lancamentos"),
            {
                "termo": self.termo.pk,
                "situacao": Lancamento.Situacao.REGULAR,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["total_lancamentos"],
            2,
        )
        self.assertEqual(
            response.context["termo_filtro"],
            str(self.termo.pk),
        )
        self.assertEqual(
            response.context["situacao_filtro"],
            Lancamento.Situacao.REGULAR,
        )

