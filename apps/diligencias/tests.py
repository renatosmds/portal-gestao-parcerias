from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

class DiligenciasRoutesTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("teste_s19", "teste@example.com", "senha-forte")
        self.client.force_login(self.user)

    def test_listagem_renderiza_conteudo(self):
        response = self.client.get(reverse("list_diligencias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Central de Diligências")
        self.assertContains(response, "Nova diligência")

    def test_cadastro_abre(self):
        response = self.client.get(reverse("create_diligencia"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nova diligência")
