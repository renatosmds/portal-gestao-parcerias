from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class Sprint32AccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin_sprint32",
            email="admin@example.com",
            password="Teste@123",
        )
        self.client.force_login(self.user)

    def test_rotas_administrativas_nao_negam_superusuario(self):
        nomes = [
            "list_empresas",
            "list_funcionarios",
            "folhas_ponto_list",
            "folhas_pagamento_list",
            "list_hora_extra",
            "list_curso",
            "execucao_em_desenvolvimento",
            "financeiro_em_desenvolvimento",
        ]
        for nome in nomes:
            with self.subTest(nome=nome):
                response = self.client.get(reverse(nome))
                self.assertNotIn(response.status_code, (403, 500))
