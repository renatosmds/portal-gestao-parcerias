from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from apps.importacoes.models import Importacao

class ImportacoesTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "admin",
            password="x",
            is_staff=True,
        )

        permissao = Permission.objects.get(
            content_type__app_label="importacoes",
            codename="view_importacao",
        )

        self.user.user_permissions.add(
            permissao
        )

        self.client.force_login(
            self.user
        )
    def test_lista_abre(self):
        self.assertEqual(self.client.get(reverse("list_importacoes")).status_code, 200)
    def test_nova_abre_para_staff(self):
        self.assertEqual(self.client.get(reverse("create_importacao")).status_code, 200)
    def test_modelo(self):
        obj = Importacao.objects.create(tipo="osc", arquivo_nome="teste.csv", criado_por=self.user)
        self.assertEqual(obj.situacao, "validacao")


class ImportacoesPermissaoModuloTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="usuario_sem_importacoes",
            password="teste12345",
        )

    def test_usuario_sem_modulo_nao_acessa_lista_por_url(self):
        self.client.force_login(
            self.usuario
        )

        response = self.client.get(
            reverse("list_importacoes")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_usuario_com_view_importacao_acessa_lista(self):
        permissao = Permission.objects.get(
            content_type__app_label="importacoes",
            codename="view_importacao",
        )

        self.usuario.user_permissions.add(
            permissao
        )

        self.client.force_login(
            self.usuario
        )

        response = self.client.get(
            reverse("list_importacoes")
        )

        self.assertEqual(
            response.status_code,
            200,
        )
