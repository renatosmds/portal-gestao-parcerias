from django.contrib.auth.models import Group, Permission, User
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

    def test_gestor_municipal_visualiza_todas_as_empresas(self):
        outra_empresa = Empresa.objects.create(
            nome="Empresa Global Gestor"
        )

        gestor = User.objects.create_user(
            username="gestor_empresas",
            password="senha-teste-123",
        )

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal"
        )

        gestor.groups.add(
            grupo
        )

        permissao = Permission.objects.get(
            content_type__app_label="empresas",
            codename="view_empresa",
        )

        gestor.user_permissions.add(
            permissao
        )

        self.client.force_login(
            gestor
        )

        response = self.client.get(
            reverse("list_empresas")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["total_empresas"],
            2,
        )

        self.assertContains(
            response,
            self.empresa.nome,
        )

        self.assertContains(
            response,
            outra_empresa.nome,
        )

        self.assertTrue(
            response.context[
                "pode_ver_todas_empresas"
            ]
        )

    def test_usuario_comum_sem_empresa_nao_recebe_visao_global(self):
        usuario = User.objects.create_user(
            username="usuario_empresas_restrito",
            password="senha-teste-123",
        )

        permissao = Permission.objects.get(
            content_type__app_label="empresas",
            codename="view_empresa",
        )

        usuario.user_permissions.add(
            permissao
        )

        self.client.force_login(
            usuario
        )

        response = self.client.get(
            reverse("list_empresas")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.context["total_empresas"],
            0,
        )

        self.assertFalse(
            response.context[
                "pode_ver_todas_empresas"
            ]
        )

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
