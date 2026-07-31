from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.termos.models import Termos


class TermosAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Termo")
        cls.termo = Termos.objects.create(
            termo="TC 001/2026",
            nomeosc="OSC Teste",
            empresa=cls.empresa,
        )
        cls.user = User.objects.create_user(
            username="termo_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        self.assertEqual(self.client.get(reverse("list_termos")).status_code, 302)

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("list_termos")).status_code, 403)

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_termo",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("list_termos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TC 001/2026")

    def test_str_nunca_retorna_none(self):
        vazio = Termos.objects.create(empresa=self.empresa)
        self.assertEqual(str(vazio), f"Termo #{vazio.pk}")
