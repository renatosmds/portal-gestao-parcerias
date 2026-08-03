from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.treinamento.models import ProgressoTreinamento


class TreinamentoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="aluno", password="Teste@123"
        )
        self.client.force_login(self.user)

    def test_painel_abre(self):
        response = self.client.get(reverse("treinamento_painel"))
        self.assertEqual(response.status_code, 200)

    def test_modulo_abre(self):
        response = self.client.get(
            reverse("treinamento_modulo", args=["primeiros-passos"])
        )
        self.assertEqual(response.status_code, 200)

    def test_concluir_modulo(self):
        response = self.client.post(
            reverse("treinamento_concluir", args=["primeiros-passos"]),
            {"concluido": "1"},
        )
        self.assertEqual(response.status_code, 302)
        progresso = ProgressoTreinamento.objects.get(
            usuario=self.user, modulo="primeiros-passos"
        )
        self.assertTrue(progresso.concluido)
