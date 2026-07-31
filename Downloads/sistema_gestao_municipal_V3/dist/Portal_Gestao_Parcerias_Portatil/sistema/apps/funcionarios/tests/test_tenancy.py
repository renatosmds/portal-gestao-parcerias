from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario


class FuncionariosTenantTest(TestCase):
    """
    Testes-base do isolamento por empresa.

    Talvez seja necessário completar os campos obrigatórios de Empresa e
    Funcionario conforme as regras específicas do seu projeto.
    """

    @classmethod
    def setUpTestData(cls):
        # Ajuste os campos obrigatórios de Empresa se o seu model exigir mais dados.
        cls.empresa_a = Empresa.objects.create(nome="Empresa A")
        cls.empresa_b = Empresa.objects.create(nome="Empresa B")

        cls.user_a = User.objects.create_user(
            username="usuario_a",
            password="senha-teste",
        )
        cls.user_b = User.objects.create_user(
            username="usuario_b",
            password="senha-teste",
        )

    def test_lista_exige_login(self):
        response = self.client.get(reverse("list_funcionarios"))
        self.assertEqual(response.status_code, 302)

    # Ative os testes abaixo depois de completar os campos obrigatórios
    # necessários à criação de Funcionario no seu banco.
