from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.departamentos.models import Departamento
from apps.empresas.models import Empresa


class DepartamentoAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Teste")
        cls.departamento = Departamento.objects.create(
            nome="Departamento Teste",
            empresa=cls.empresa,
        )
        cls.user = User.objects.create_user(
            username="departamento_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        response = self.client.get(reverse("list_departamentos"))
        self.assertEqual(response.status_code, 302)

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("list_departamentos"))
        self.assertEqual(response.status_code, 403)

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_departamento",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("list_departamentos"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Departamento Teste")

    def test_superuser_abre_detalhe(self):
        admin = User.objects.create_superuser(
            username="admin_detalhe_departamento",
            email="admin2@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)

        response = self.client.get(
            reverse(
                "detail_departamento",
                kwargs={"pk": self.departamento.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Departamento Teste")

    def test_superintendencia_pode_ter_diretoria(self):
        superintendencia = Departamento.objects.create(
            nome="Superintendencia Teste",
            empresa=self.empresa,
            tipo=Departamento.Tipo.SUPERINTENDENCIA,
            superior=self.departamento,
        )

        diretoria = Departamento(
            nome="Diretoria Teste",
            empresa=self.empresa,
            tipo=Departamento.Tipo.DIRETORIA,
            superior=superintendencia,
        )

        diretoria.full_clean()

    def test_gerencia_exige_diretoria_como_superior(self):
        superintendencia = Departamento.objects.create(
            nome="Superintendencia Gerencia",
            empresa=self.empresa,
            tipo=Departamento.Tipo.SUPERINTENDENCIA,
            superior=self.departamento,
        )

        gerencia = Departamento(
            nome="Gerencia Invalida",
            empresa=self.empresa,
            tipo=Departamento.Tipo.GERENCIA,
            superior=superintendencia,
        )

        with self.assertRaises(Exception):
            gerencia.full_clean()

    def test_unidade_superior_deve_ser_da_mesma_empresa(self):
        outra_empresa = Empresa.objects.create(
            nome="Outra Empresa"
        )

        outro_departamento = Departamento.objects.create(
            nome="Departamento Outra Empresa",
            empresa=outra_empresa,
        )

        superintendencia = Departamento(
            nome="Superintendencia Cruzada",
            empresa=self.empresa,
            tipo=Departamento.Tipo.SUPERINTENDENCIA,
            superior=outro_departamento,
        )

        with self.assertRaises(Exception):
            superintendencia.full_clean()
