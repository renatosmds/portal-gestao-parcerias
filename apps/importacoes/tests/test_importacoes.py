from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from apps.importacoes.models import Importacao

class ImportacoesTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("admin", password="x", is_staff=True)
        self.client.force_login(self.user)
    def test_lista_abre(self):
        self.assertEqual(self.client.get(reverse("list_importacoes")).status_code, 200)
    def test_nova_abre_para_staff(self):
        self.assertEqual(self.client.get(reverse("create_importacao")).status_code, 200)
    def test_modelo(self):
        obj = Importacao.objects.create(tipo="osc", arquivo_nome="teste.csv", criado_por=self.user)
        self.assertEqual(obj.situacao, "validacao")
