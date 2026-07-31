from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from apps.prestacao.models import Prestacao
from .models import MetaExecucao

class MetasTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="teste", password="123", is_staff=True)
        self.prestacao = Prestacao.objects.create(tipo="cnpj", numtermo="TC 001/2026")
    def test_painel_exige_login(self):
        self.assertEqual(self.client.get(reverse("metas_painel")).status_code, 302)
    def test_painel_abre_para_usuario_autenticado(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("metas_painel")).status_code, 200)
    def test_percentual_execucao(self):
        meta = MetaExecucao.objects.create(prestacao=self.prestacao, titulo="Atendimentos", valor_previsto=100, valor_realizado=75)
        self.assertEqual(float(meta.percentual_execucao), 75.0)
