from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.parcerias.models import Parcerias


class ParceriaAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Parceria")
        cls.parceria = Parcerias.objects.create(
            nomeOSC="OSC Teste",
            empresa=cls.empresa,
        )
        cls.user = User.objects.create_user(
            username="parceria_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        response = self.client.get(reverse("list_parcerias"))
        self.assertEqual(response.status_code, 302)

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("list_parcerias"))
        self.assertEqual(response.status_code, 403)

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_parceria",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("list_parcerias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OSC Teste")

    def test_superuser_abre_detalhe(self):
        admin = User.objects.create_superuser(
            username="admin_detalhe_parceria",
            email="admin2@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(
            reverse("detail_parceria", kwargs={"pk": self.parceria.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OSC Teste")
