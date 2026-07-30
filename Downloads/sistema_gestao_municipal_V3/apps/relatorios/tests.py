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
