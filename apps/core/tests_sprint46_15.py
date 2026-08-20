from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.test import TestCase

from apps.core.permissoes_modulos import (
    MODULOS,
    modulo_liberado,
    modulos_liberados,
)


class Sprint4615ControleModulosTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="usuario_sprint4615",
            password="senha-forte-4615",
        )

        self.superusuario = User.objects.create_superuser(
            username="admin_sprint4615",
            email="admin@example.com",
            password="senha-forte-4615",
        )

    def _conceder(self, usuario, app_label, codename):
        permissao = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )
        usuario.user_permissions.add(permissao)

        # Limpa eventual cache de permissoes do Django.
        for atributo in (
            "_perm_cache",
            "_user_perm_cache",
            "_group_perm_cache",
        ):
            if hasattr(usuario, atributo):
                delattr(usuario, atributo)

        return permissao

    def test_usuario_sem_permissao_nao_possui_modulo(self):
        self.assertFalse(
            modulo_liberado(self.usuario, "pareceres")
        )

    def test_permissao_direta_libera_modulo(self):
        self._conceder(
            self.usuario,
            "pareceres",
            "view_parecertecnico",
        )

        self.assertTrue(
            modulo_liberado(self.usuario, "pareceres")
        )

    def test_permissao_por_grupo_libera_modulo(self):
        grupo = Group.objects.create(name="Analistas Sprint 46.15")

        permissao = Permission.objects.get(
            content_type__app_label="conciliacao",
            codename="view_conciliacao",
        )

        grupo.permissions.add(permissao)
        self.usuario.groups.add(grupo)

        self.assertTrue(
            modulo_liberado(self.usuario, "conciliacao")
        )

    def test_superusuario_possui_todos_os_modulos(self):
        for modulo in MODULOS:
            with self.subTest(modulo=modulo):
                self.assertTrue(
                    modulo_liberado(self.superusuario, modulo)
                )

    def test_permissao_de_um_modulo_nao_libera_outro(self):
        self._conceder(
            self.usuario,
            "pareceres",
            "view_parecertecnico",
        )

        self.assertTrue(
            modulo_liberado(self.usuario, "pareceres")
        )

        self.assertFalse(
            modulo_liberado(self.usuario, "conciliacao")
        )

    def test_varios_modulos_podem_ser_liberados(self):
        self._conceder(
            self.usuario,
            "pareceres",
            "view_parecertecnico",
        )
        self._conceder(
            self.usuario,
            "metas",
            "view_metaexecucao",
        )

        liberados = modulos_liberados(self.usuario)

        self.assertIn("pareceres", liberados)
        self.assertIn("metas", liberados)
        self.assertNotIn("conciliacao", liberados)

    def test_relatorios_e_liberado_por_permissao_de_fonte(self):
        self._conceder(
            self.usuario,
            "diligencias",
            "view_diligencia",
        )

        self.assertTrue(
            modulo_liberado(self.usuario, "relatorios")
        )

    def test_modulo_inexistente_nao_e_liberado(self):
        self.assertFalse(
            modulo_liberado(
                self.usuario,
                "modulo_inexistente",
            )
        )

    def test_usuario_anonimo_nao_possui_modulos(self):
        self.assertEqual(
            modulos_liberados(AnonymousUser()),
            set(),
        )

class Sprint4615ProtecaoURLTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="usuario_url_4615",
            password="senha-url-4615",
        )
        self.client.force_login(self.usuario)

    def _conceder(self, app_label, codename):
        permissao = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )
        self.usuario.user_permissions.add(permissao)

        for atributo in (
            "_perm_cache",
            "_user_perm_cache",
            "_group_perm_cache",
        ):
            if hasattr(self.usuario, atributo):
                delattr(self.usuario, atributo)

    def test_pareceres_sem_permissao_retorna_403(self):
        from django.urls import reverse

        resposta = self.client.get(
            reverse("pareceres:parecer_lista")
        )

        self.assertEqual(resposta.status_code, 403)

    def test_pareceres_com_permissao_permite_acesso(self):
        from django.urls import reverse

        self._conceder(
            "pareceres",
            "view_parecertecnico",
        )

        resposta = self.client.get(
            reverse("pareceres:parecer_lista")
        )

        self.assertEqual(resposta.status_code, 200)

    def test_conciliacao_sem_permissao_retorna_403(self):
        from django.urls import reverse

        resposta = self.client.get(
            reverse("conciliacao_painel")
        )

        self.assertEqual(resposta.status_code, 403)

    def test_planos_trabalho_sem_permissao_retorna_403(self):
        from django.urls import reverse

        resposta = self.client.get(
            reverse("planos_trabalho:plano_lista")
        )

        self.assertEqual(resposta.status_code, 403)

class Sprint4615MenuPorUsuarioTests(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()

        self.usuario = UserModel.objects.create_user(
            username="usuario_menu_4615",
            password="senha-menu-4615",
        )

        self.client.force_login(self.usuario)

    def _permissao(self, app_label, codename):
        return Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )

    def _limpar_cache_permissoes(self):
        for atributo in (
            "_perm_cache",
            "_user_perm_cache",
            "_group_perm_cache",
        ):
            if hasattr(self.usuario, atributo):
                delattr(self.usuario, atributo)

    def _home(self):
        from django.urls import reverse
        return self.client.get(reverse("home"))

    def test_menu_nao_exibe_pareceres_sem_permissao(self):
        from django.urls import reverse

        resposta = self._home()

        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(
            resposta,
            f'href="{reverse("pareceres:parecer_lista")}"',
        )

    def test_menu_exibe_pareceres_com_permissao_direta(self):
        from django.urls import reverse

        permissao = self._permissao(
            "pareceres",
            "view_parecertecnico",
        )

        self.usuario.user_permissions.add(permissao)
        self._limpar_cache_permissoes()

        resposta = self._home()

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(
            resposta,
            f'href="{reverse("pareceres:parecer_lista")}"',
        )

    def test_menu_exibe_pareceres_com_permissao_por_grupo(self):
        from django.contrib.auth.models import Group
        from django.urls import reverse

        grupo = Group.objects.create(
            name="Pareceristas Sprint 46.15"
        )

        permissao = self._permissao(
            "pareceres",
            "view_parecertecnico",
        )

        grupo.permissions.add(permissao)
        self.usuario.groups.add(grupo)
        self._limpar_cache_permissoes()

        resposta = self._home()

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(
            resposta,
            f'href="{reverse("pareceres:parecer_lista")}"',
        )

    def test_permissao_pareceres_nao_exibe_conciliacao(self):
        from django.urls import reverse

        permissao = self._permissao(
            "pareceres",
            "view_parecertecnico",
        )

        self.usuario.user_permissions.add(permissao)
        self._limpar_cache_permissoes()

        resposta = self._home()

        self.assertContains(
            resposta,
            f'href="{reverse("pareceres:parecer_lista")}"',
        )

        self.assertNotContains(
            resposta,
            f'href="{reverse("conciliacao_painel")}"',
        )

    def test_superusuario_visualiza_modulos_controlados(self):
        from django.contrib.auth import get_user_model
        from django.urls import reverse

        UserModel = get_user_model()

        admin = UserModel.objects.create_superuser(
            username="admin_menu_4615",
            email="admin4615@example.com",
            password="senha-admin-4615",
        )

        self.client.force_login(admin)

        resposta = self.client.get(reverse("home"))

        self.assertEqual(resposta.status_code, 200)

        urls = (
            reverse("pareceres:parecer_lista"),
            reverse("conciliacao_painel"),
            reverse("planos_trabalho:plano_lista"),
            reverse("relatorios_painel"),
        )

        for url in urls:
            with self.subTest(url=url):
                self.assertContains(
                    resposta,
                    f'href="{url}"',
                )

class Sprint4615DashboardPermissoesTests(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()

        self.usuario = UserModel.objects.create_user(
            username="usuario_dashboard_4615",
            password="senha-dashboard-4615",
            is_staff=True,
        )

        self.client.force_login(self.usuario)

    def _conceder(self, app_label, codename):
        permissao = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )

        self.usuario.user_permissions.add(permissao)

        for atributo in (
            "_perm_cache",
            "_user_perm_cache",
            "_group_perm_cache",
        ):
            if hasattr(self.usuario, atributo):
                delattr(self.usuario, atributo)

    def _contexto_home(self):
        from django.urls import reverse

        resposta = self.client.get(reverse("home"))

        self.assertEqual(resposta.status_code, 200)

        return resposta.context

    def test_dashboard_sem_permissoes_nao_disponibiliza_modulos(self):
        contexto = self._contexto_home()

        self.assertEqual(
            tuple(contexto["dashboard_modulos"]),
            (),
        )

    def test_dashboard_recebe_apenas_modulo_autorizado(self):
        self._conceder(
            "pareceres",
            "view_parecertecnico",
        )

        contexto = self._contexto_home()

        self.assertIn(
            "pareceres",
            contexto["dashboard_modulos"],
        )

        self.assertNotIn(
            "diligencias",
            contexto["dashboard_modulos"],
        )

    def test_dashboard_sem_diligencias_nao_expoe_alertas_diligencias(self):
        contexto = self._contexto_home()

        modulos_alertas = {
            alerta["modulo"]
            for alerta in contexto["alertas_dashboard"]
        }

        self.assertNotIn(
            "diligencias",
            modulos_alertas,
        )

    def test_dashboard_com_diligencias_pode_expor_alertas_diligencias(self):
        self._conceder(
            "diligencias",
            "view_diligencia",
        )

        contexto = self._contexto_home()

        modulos_alertas = {
            alerta["modulo"]
            for alerta in contexto["alertas_dashboard"]
        }

        self.assertIn(
            "diligencias",
            modulos_alertas,
        )

class Sprint4615DashboardVisualTests(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model

        UserModel = get_user_model()

        self.usuario = UserModel.objects.create_user(
            username="usuario_dashboard_visual_4615",
            password="senha-dashboard-visual-4615",
            is_staff=True,
        )

        self.client.force_login(self.usuario)

    def _conceder(self, app_label, codename):
        permissao = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename,
        )

        self.usuario.user_permissions.add(permissao)

        for atributo in (
            "_perm_cache",
            "_user_perm_cache",
            "_group_perm_cache",
        ):
            if hasattr(self.usuario, atributo):
                delattr(self.usuario, atributo)

    def _home(self):
        from django.urls import reverse

        resposta = self.client.get(reverse("home"))

        self.assertEqual(resposta.status_code, 200)

        return resposta

    def test_dashboard_sem_modulos_exibe_mensagem(self):
        resposta = self._home()

        self.assertContains(
            resposta,
            'id="dashboard-sem-modulos"',
        )

    def test_dashboard_sem_diligencias_nao_exibe_atalho_diligencias(self):
        from django.urls import reverse

        resposta = self._home()

        self.assertNotContains(
            resposta,
            f'href="{reverse("list_diligencias")}"',
        )

    def test_dashboard_com_diligencias_exibe_atalho_diligencias(self):
        from django.urls import reverse

        self._conceder(
            "diligencias",
            "view_diligencia",
        )

        resposta = self._home()

        self.assertContains(
            resposta,
            f'href="{reverse("list_diligencias")}"',
        )

    def test_dashboard_com_prestacao_exibe_atalho_prestacao(self):
        from django.urls import reverse

        self._conceder(
            "prestacao",
            "view_prestacao",
        )

        resposta = self._home()

        self.assertContains(
            resposta,
            f'href="{reverse("list_prestacao")}"',
        )

    def test_dashboard_pareceres_nao_libera_diligencias(self):
        from django.urls import reverse

        self._conceder(
            "pareceres",
            "view_parecertecnico",
        )

        resposta = self._home()

        self.assertNotContains(
            resposta,
            f'href="{reverse("list_diligencias")}"',
        )

    def test_superusuario_nao_recebe_mensagem_sem_modulos(self):
        from django.contrib.auth import get_user_model
        from django.urls import reverse

        UserModel = get_user_model()

        admin = UserModel.objects.create_superuser(
            username="admin_dashboard_visual_4615",
            email="admin-dashboard-4615@example.com",
            password="senha-admin-dashboard-4615",
        )

        self.client.force_login(admin)

        resposta = self.client.get(reverse("home"))

        self.assertEqual(resposta.status_code, 200)

        self.assertNotContains(
            resposta,
            'id="dashboard-sem-modulos"',
        )
