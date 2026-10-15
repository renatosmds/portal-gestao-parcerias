from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

class RelatoriosRoutesTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("teste_relatorios", "relatorios@example.com", "senha-forte")
        self.client.force_login(self.user)
    def test_painel(self):
        response=self.client.get(reverse("relatorios_painel"))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"Central de Relatórios")
    def test_csv_diligencias(self):
        response=self.client.get(reverse("relatorio_diligencias_csv"))
        self.assertEqual(response.status_code,200)
        self.assertIn("text/csv",response["Content-Type"])



class RelatoriosPermissoesPorFonteTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Permission

        User = get_user_model()

        self.user = User.objects.create_user(
            username="relatorios_restrito",
            password="senha-forte",
        )

        self.view_diligencia = Permission.objects.get(
            content_type__app_label="diligencias",
            codename="view_diligencia",
        )

        self.view_lancamento = Permission.objects.get(
            content_type__app_label="lancamentos",
            codename="view_lancamento",
        )

        self.view_funcionario = Permission.objects.get(
            content_type__app_label="funcionarios",
            codename="view_funcionario",
        )

        self.view_folha = Permission.objects.get(
            content_type__app_label="funcionarios",
            codename="view_folhapagamento",
        )

        self.client.force_login(
            self.user
        )

    def test_apenas_diligencias_nao_abre_outros_relatorios(self):
        self.user.user_permissions.add(
            self.view_diligencia
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorios_painel")
            ).status_code,
            200,
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_diligencias")
            ).status_code,
            200,
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_glosas")
            ).status_code,
            403,
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_funcionarios")
            ).status_code,
            403,
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_folha")
            ).status_code,
            403,
        )

    def test_apenas_glosas_nao_abre_outros_relatorios(self):
        self.user.user_permissions.add(
            self.view_lancamento
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_glosas")
            ).status_code,
            200,
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_diligencias")
            ).status_code,
            403,
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_funcionarios")
            ).status_code,
            403,
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_folha")
            ).status_code,
            403,
        )

    def test_funcionario_e_folha_exigem_permissoes_independentes(self):
        self.user.user_permissions.add(
            self.view_funcionario
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_funcionarios")
            ).status_code,
            200,
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_folha")
            ).status_code,
            403,
        )

        self.user.user_permissions.add(
            self.view_folha
        )

        self.assertEqual(
            self.client.get(
                reverse("relatorio_folha")
            ).status_code,
            200,
        )

    def test_painel_exibe_somente_card_autorizado(self):
        self.user.user_permissions.add(
            self.view_diligencia
        )

        response = self.client.get(
            reverse("relatorios_painel")
        )

        self.assertContains(
            response,
            "Diligências",
        )

        self.assertNotContains(
            response,
            "Abrir demonstrativo",
        )

        self.assertNotContains(
            response,
            ">Funcionários<",
            html=False,
        )
