from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.analise.models import Analise
from apps.empresas.models import Empresa
from apps.termos.models import Termos


class AnaliseAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Análise")
        cls.termo = Termos.objects.create(
            termo="TC 001/2026",
            empresa=cls.empresa,
        )
        cls.analise = Analise.objects.create(
            numtermo=cls.termo,
            nomeOSC="OSC Teste",
            item="1",
            inconformidade="Inconformidade de teste",
            empresa=cls.empresa,
        )
        cls.user = User.objects.create_user(
            username="analise_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        self.assertEqual(
            self.client.get(reverse("list_analise")).status_code,
            302,
        )

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("list_analise")).status_code,
            403,
        )

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_analise",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("list_analise"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OSC Teste")

    def test_str_nunca_retorna_none(self):
        item = Analise.objects.create(empresa=self.empresa)
        self.assertEqual(str(item), f"Análise #{item.pk}")
