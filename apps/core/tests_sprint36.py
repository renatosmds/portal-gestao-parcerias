from django.contrib.auth import get_user_model
from django.test import TestCase


class DashboardExecutivoSprint36Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.usuario = User.objects.create_user(
            username="teste_sprint36",
            password="SenhaTeste123!",
            is_staff=True,
            is_superuser=True,
        )

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_dashboard_carrega_com_sucesso(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/index.html")

    def test_contexto_indicadores_financeiros(self):
        response = self.client.get("/")

        campos = [
            "valor_global",
            "valor_executado",
            "saldo_a_executar",
            "percentual_execucao",
        ]

        for campo in campos:
            with self.subTest(campo=campo):
                self.assertIn(campo, response.context)

    def test_contexto_fluxo_prestacao_contas(self):
        response = self.client.get("/")

        campos = [
            "prestacoes_total",
            "prestacoes_elaboracao",
            "prestacoes_enviadas",
            "prestacoes_recebidas",
            "prestacoes_em_analise",
            "prestacoes_em_diligencia",
            "prestacoes_corrigidas",
            "prestacoes_aprovadas",
            "prestacoes_aprovadas_ressalvas",
            "prestacoes_reprovadas",
            "prestacoes_encerradas",
        ]

        for campo in campos:
            with self.subTest(campo=campo):
                self.assertIn(campo, response.context)

    def test_contexto_alertas_diligencias(self):
        response = self.client.get("/")

        campos = [
            "diligencias_pendentes",
            "diligencias_vencidas",
            "diligencias_proximas_vencimento",
            "diligencias_urgentes",
        ]

        for campo in campos:
            with self.subTest(campo=campo):
                self.assertIn(campo, response.context)

    def test_contexto_execucao_fisica_metas(self):
        response = self.client.get("/")

        campos = [
            "metas_total",
            "metas_nao_iniciadas",
            "metas_em_andamento",
            "metas_atingidas",
            "metas_parciais",
            "metas_nao_atingidas",
            "metas_suspensas",
            "metas_criticas",
            "metas_atrasadas",
            "percentual_metas_atingidas",
        ]

        for campo in campos:
            with self.subTest(campo=campo):
                self.assertIn(campo, response.context)

    def test_dashboard_exibe_secoes_sprint36(self):
        response = self.client.get("/")

        self.assertContains(response, "FLUXO DA PRESTAÇÃO DE CONTAS")
        self.assertContains(response, "EXECUÇÃO FÍSICA")
        self.assertContains(response, "Metas da parceria")

    def test_dashboard_sem_dados_retorna_indicadores_zero(self):
        response = self.client.get("/")

        self.assertEqual(response.context["metas_total"], 0)
        self.assertEqual(response.context["metas_atingidas"], 0)
        self.assertEqual(response.context["metas_atrasadas"], 0)
        self.assertEqual(response.context["percentual_metas_atingidas"], 0)
