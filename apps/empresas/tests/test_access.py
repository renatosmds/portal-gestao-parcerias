from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa


class EmpresaAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Teste")
        cls.user = User.objects.create_user(
            username="empresa_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        response = self.client.get(reverse("list_empresas"))
        self.assertEqual(response.status_code, 302)

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("list_empresas"))
        self.assertEqual(response.status_code, 403)

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_empresa",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("list_empresas"))
        self.assertEqual(response.status_code, 200)

    def test_superuser_abre_detalhe(self):
        admin = User.objects.create_superuser(
            username="admin_detalhe",
            email="admin2@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(
            reverse("detail_empresa", kwargs={"pk": self.empresa.pk})
        )
        self.assertEqual(response.status_code, 200)
