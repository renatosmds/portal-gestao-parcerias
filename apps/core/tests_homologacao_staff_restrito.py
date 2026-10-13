from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse


class StaffRestritoHomologacaoTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="staff_restrito_regressao",
            password="teste123",
            is_staff=True,
            is_superuser=False,
        )

        self.client.force_login(
            self.usuario
        )

    def test_staff_sem_permissao_nao_acessa_diagnostico(self):
        response = self.client.get(
            reverse("diagnostico_portal")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_staff_sem_permissao_nao_acessa_gestao_transparencia(self):
        response = self.client.get(
            reverse("transparencia_painel")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_staff_sem_permissao_nao_ve_links_administrativos(self):
        response = self.client.get(
            reverse("home")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotContains(
            response,
            reverse("diagnostico_portal"),
        )

        self.assertNotContains(
            response,
            reverse("transparencia_painel"),
        )

    def test_portal_publico_continua_publico(self):
        response = self.client.get(
            reverse("transparencia_publica")
        )

        self.assertEqual(
            response.status_code,
            200,
        )


class TransparenciaPermissoesHomologacaoTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="usuario_transparencia",
            password="teste123",
        )

        self.client.force_login(
            self.usuario
        )

    def conceder(self, *codenames):
        permissoes = Permission.objects.filter(
            content_type__app_label="transparencia",
            codename__in=codenames,
        )

        self.usuario.user_permissions.add(
            *permissoes
        )

    def test_view_libera_painel_transparencia(self):
        self.conceder(
            "view_publicacaoparceria"
        )

        response = self.client.get(
            reverse("transparencia_painel")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_view_nao_concede_change(self):
        self.conceder(
            "view_publicacaoparceria"
        )

        self.assertFalse(
            self.usuario.has_perm(
                "transparencia.change_publicacaoparceria"
            )
        )

    def test_staff_nao_eh_administrador_sistema(self):
        self.usuario.is_staff = True
        self.usuario.save(
            update_fields=["is_staff"]
        )

        response = self.client.get(
            reverse("diagnostico_portal")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_grupo_admin_acessa_diagnostico(self):
        grupo = Group.objects.create(
            name="Administrador do Sistema"
        )

        self.usuario.groups.add(
            grupo
        )

        response = self.client.get(
            reverse("diagnostico_portal")
        )

        self.assertEqual(
            response.status_code,
            200,
        )
