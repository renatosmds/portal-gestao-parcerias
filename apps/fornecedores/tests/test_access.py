from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.fornecedores.models import Fornecedores


class FornecedorAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Fornecedor")
        cls.fornecedor = Fornecedores.objects.create(
            credor="Fornecedor Teste",
            pessoa="jurídica",
            tipo="cnpj",
            numero="00.000.000/0001-00",
            empresa=cls.empresa,
        )
        cls.user = User.objects.create_user(
            username="fornecedor_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        response = self.client.get(reverse("list_fornecedores"))
        self.assertEqual(response.status_code, 302)

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("list_fornecedores"))
        self.assertEqual(response.status_code, 403)

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_fornecedor",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("list_fornecedores"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fornecedor Teste")

    def test_superuser_abre_detalhe(self):
        admin = User.objects.create_superuser(
            username="admin_detalhe_fornecedor",
            email="admin2@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)

        response = self.client.get(
            reverse(
                "detail_fornecedor",
                kwargs={"pk": self.fornecedor.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fornecedor Teste")
