from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from apps.core.permissoes_modulos import MODULOS


User = get_user_model()


class Sprint4618ModelosDashboardTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="usuario_dashboard_4618",
            password="teste123",
        )

        self.grupo = Group.objects.create(
            name="Grupo Dashboard 46.18",
        )

    def test_configuracao_usuario_aceita_estado_herdar(self):
        from apps.core.models import ConfiguracaoDashboardUsuario

        config = ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.HERDAR,
        )

        self.assertEqual(
            config.estado,
            ConfiguracaoDashboardUsuario.Estado.HERDAR,
        )

    def test_configuracao_usuario_aceita_estado_mostrar(self):
        from apps.core.models import ConfiguracaoDashboardUsuario

        config = ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.MOSTRAR,
        )

        self.assertEqual(
            config.estado,
            ConfiguracaoDashboardUsuario.Estado.MOSTRAR,
        )

    def test_configuracao_usuario_aceita_estado_ocultar(self):
        from apps.core.models import ConfiguracaoDashboardUsuario

        config = ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.OCULTAR,
        )

        self.assertEqual(
            config.estado,
            ConfiguracaoDashboardUsuario.Estado.OCULTAR,
        )

    def test_nao_permite_duplicar_usuario_modulo(self):
        from apps.core.models import ConfiguracaoDashboardUsuario

        ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.MOSTRAR,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ConfiguracaoDashboardUsuario.objects.create(
                    usuario=self.usuario,
                    modulo="parcerias",
                    estado=ConfiguracaoDashboardUsuario.Estado.OCULTAR,
                )

    def test_configuracao_grupo_pode_exibir(self):
        from apps.core.models import ConfiguracaoDashboardGrupo

        config = ConfiguracaoDashboardGrupo.objects.create(
            grupo=self.grupo,
            modulo="parcerias",
            exibir=True,
        )

        self.assertTrue(config.exibir)

    def test_configuracao_grupo_pode_ocultar(self):
        from apps.core.models import ConfiguracaoDashboardGrupo

        config = ConfiguracaoDashboardGrupo.objects.create(
            grupo=self.grupo,
            modulo="parcerias",
            exibir=False,
        )

        self.assertFalse(config.exibir)

    def test_nao_permite_duplicar_grupo_modulo(self):
        from apps.core.models import ConfiguracaoDashboardGrupo

        ConfiguracaoDashboardGrupo.objects.create(
            grupo=self.grupo,
            modulo="parcerias",
            exibir=True,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ConfiguracaoDashboardGrupo.objects.create(
                    grupo=self.grupo,
                    modulo="parcerias",
                    exibir=False,
                )

    def test_modulo_configurado_existe_na_matriz_central(self):
        self.assertIn(
            "parcerias",
            MODULOS,
        )

class Sprint4618RegraDashboardTests(TestCase):

    def setUp(self):
        from django.contrib.auth.models import Permission

        self.usuario = User.objects.create_user(
            username="usuario_regra_dashboard_4618",
            password="teste123",
        )

        self.grupo = Group.objects.create(
            name="Grupo Regra Dashboard 46.18",
        )

        self.permissao_parcerias = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        self.permissao_documentos = Permission.objects.get(
            content_type__app_label="documentos",
            codename="view_documento",
        )

    def test_sem_configuracao_preserva_comportamento_atual(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )

        self.usuario.user_permissions.add(
            self.permissao_parcerias
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertIn(
            "parcerias",
            resultado,
        )

    def test_individual_ocultar_prevalece(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )
        from apps.core.models import (
            ConfiguracaoDashboardUsuario,
        )

        self.usuario.user_permissions.add(
            self.permissao_parcerias
        )

        ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.OCULTAR,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "parcerias",
            resultado,
        )

    def test_individual_mostrar_exibe_modulo_autorizado(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )
        from apps.core.models import (
            ConfiguracaoDashboardUsuario,
        )

        self.usuario.user_permissions.add(
            self.permissao_parcerias
        )

        ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.MOSTRAR,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertIn(
            "parcerias",
            resultado,
        )

    def test_dashboard_nao_concede_acesso_sem_permissao(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )
        from apps.core.models import (
            ConfiguracaoDashboardUsuario,
        )

        ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.MOSTRAR,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "parcerias",
            resultado,
        )

    def test_grupo_exibir_habilita_dashboard(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )
        from apps.core.models import (
            ConfiguracaoDashboardGrupo,
        )

        self.grupo.permissions.add(
            self.permissao_parcerias
        )

        self.usuario.groups.add(
            self.grupo
        )

        ConfiguracaoDashboardGrupo.objects.create(
            grupo=self.grupo,
            modulo="parcerias",
            exibir=True,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertIn(
            "parcerias",
            resultado,
        )

    def test_grupo_ocultar_remove_do_dashboard(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )
        from apps.core.models import (
            ConfiguracaoDashboardGrupo,
        )

        self.grupo.permissions.add(
            self.permissao_parcerias
        )

        self.usuario.groups.add(
            self.grupo
        )

        ConfiguracaoDashboardGrupo.objects.create(
            grupo=self.grupo,
            modulo="parcerias",
            exibir=False,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "parcerias",
            resultado,
        )

    def test_um_grupo_exibir_prevalece_sobre_outro_ocultar(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )
        from apps.core.models import (
            ConfiguracaoDashboardGrupo,
        )

        outro_grupo = Group.objects.create(
            name="Outro Grupo Dashboard 46.18",
        )

        self.grupo.permissions.add(
            self.permissao_parcerias
        )

        outro_grupo.permissions.add(
            self.permissao_parcerias
        )

        self.usuario.groups.add(
            self.grupo,
            outro_grupo,
        )

        ConfiguracaoDashboardGrupo.objects.create(
            grupo=self.grupo,
            modulo="parcerias",
            exibir=False,
        )

        ConfiguracaoDashboardGrupo.objects.create(
            grupo=outro_grupo,
            modulo="parcerias",
            exibir=True,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertIn(
            "parcerias",
            resultado,
        )

    def test_individual_ocultar_prevalece_sobre_grupo_exibir(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )
        from apps.core.models import (
            ConfiguracaoDashboardGrupo,
            ConfiguracaoDashboardUsuario,
        )

        self.grupo.permissions.add(
            self.permissao_parcerias
        )

        self.usuario.groups.add(
            self.grupo
        )

        ConfiguracaoDashboardGrupo.objects.create(
            grupo=self.grupo,
            modulo="parcerias",
            exibir=True,
        )

        ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.OCULTAR,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "parcerias",
            resultado,
        )

class Sprint4618IntegracaoDashboardTests(TestCase):

    def setUp(self):
        from django.contrib.auth.models import Permission

        self.usuario = User.objects.create_user(
            username="usuario_integracao_dashboard_4618",
            password="teste123",
        )

        self.permissao_parcerias = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        self.usuario.user_permissions.add(
            self.permissao_parcerias
        )

    def test_dashboard_preserva_modulo_sem_configuracao(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertIn(
            "parcerias",
            resultado,
        )

    def test_dashboard_oculta_modulo_configurado_individualmente(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )
        from apps.core.models import (
            ConfiguracaoDashboardUsuario,
        )

        ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.OCULTAR,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "parcerias",
            resultado,
        )

    def test_dashboard_modulos_nunca_contem_modulo_sem_permissao(self):
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )
        from apps.core.models import (
            ConfiguracaoDashboardUsuario,
        )

        ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="documentos",
            estado=ConfiguracaoDashboardUsuario.Estado.MOSTRAR,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "documentos",
            resultado,
        )

class Sprint4618MatrizVisualDashboardTests(TestCase):

    def setUp(self):
        from django.contrib.auth.models import Permission

        self.superuser = User.objects.create_superuser(
            username="admin_dashboard_visual_4618",
            email="admin_dashboard_visual_4618@example.com",
            password="teste123",
        )

        self.usuario = User.objects.create_user(
            username="usuario_dashboard_visual_4618",
            password="teste123",
        )

        self.staff = User.objects.create_user(
            username="staff_dashboard_visual_4618",
            password="teste123",
            is_staff=True,
        )

        self.grupo = Group.objects.create(
            name="Grupo Visual Dashboard 46.18",
        )

        self.permissao_parcerias = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        self.usuario.user_permissions.add(
            self.permissao_parcerias
        )

    def test_superusuario_acessa_matriz_dashboard(self):
        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse("dashboard_acessos_painel")
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertContains(
            resposta,
            "Matriz do Dashboard",
        )

    def test_usuario_comum_nao_acessa_matriz_dashboard(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(
            reverse("dashboard_acessos_painel")
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

    def test_staff_nao_superusuario_nao_acessa_matriz_dashboard(self):
        self.client.force_login(self.staff)

        resposta = self.client.get(
            reverse("dashboard_acessos_painel")
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

    def test_superusuario_acessa_configuracao_dashboard_usuario(self):
        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse(
                "dashboard_acessos_usuario",
                args=[self.usuario.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertContains(
            resposta,
            "Parcerias",
        )

    def test_usuario_pode_ser_configurado_como_ocultar(self):
        from apps.core.models import ConfiguracaoDashboardUsuario

        self.client.force_login(self.superuser)

        resposta = self.client.post(
            reverse(
                "dashboard_acessos_usuario",
                args=[self.usuario.pk],
            ),
            {
                "dashboard_parcerias": "ocultar",
            },
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        config = ConfiguracaoDashboardUsuario.objects.get(
            usuario=self.usuario,
            modulo="parcerias",
        )

        self.assertEqual(
            config.estado,
            ConfiguracaoDashboardUsuario.Estado.OCULTAR,
        )

    def test_usuario_pode_ser_configurado_como_mostrar(self):
        from apps.core.models import ConfiguracaoDashboardUsuario

        self.client.force_login(self.superuser)

        self.client.post(
            reverse(
                "dashboard_acessos_usuario",
                args=[self.usuario.pk],
            ),
            {
                "dashboard_parcerias": "mostrar",
            },
        )

        config = ConfiguracaoDashboardUsuario.objects.get(
            usuario=self.usuario,
            modulo="parcerias",
        )

        self.assertEqual(
            config.estado,
            ConfiguracaoDashboardUsuario.Estado.MOSTRAR,
        )

    def test_usuario_herdar_remove_configuracao_individual(self):
        from apps.core.models import ConfiguracaoDashboardUsuario

        ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="parcerias",
            estado=ConfiguracaoDashboardUsuario.Estado.OCULTAR,
        )

        self.client.force_login(self.superuser)

        self.client.post(
            reverse(
                "dashboard_acessos_usuario",
                args=[self.usuario.pk],
            ),
            {
                "dashboard_parcerias": "herdar",
            },
        )

        self.assertFalse(
            ConfiguracaoDashboardUsuario.objects.filter(
                usuario=self.usuario,
                modulo="parcerias",
            ).exists()
        )

    def test_superusuario_acessa_configuracao_dashboard_grupo(self):
        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse(
                "dashboard_acessos_grupo",
                args=[self.grupo.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

    def test_grupo_pode_configurar_modulo_como_mostrar(self):
        from apps.core.models import ConfiguracaoDashboardGrupo

        self.client.force_login(self.superuser)

        self.client.post(
            reverse(
                "dashboard_acessos_grupo",
                args=[self.grupo.pk],
            ),
            {
                "dashboard_parcerias": "mostrar",
            },
        )

        config = ConfiguracaoDashboardGrupo.objects.get(
            grupo=self.grupo,
            modulo="parcerias",
        )

        self.assertTrue(
            config.exibir
        )

    def test_grupo_pode_configurar_modulo_como_ocultar(self):
        from apps.core.models import ConfiguracaoDashboardGrupo

        self.client.force_login(self.superuser)

        self.client.post(
            reverse(
                "dashboard_acessos_grupo",
                args=[self.grupo.pk],
            ),
            {
                "dashboard_parcerias": "ocultar",
            },
        )

        config = ConfiguracaoDashboardGrupo.objects.get(
            grupo=self.grupo,
            modulo="parcerias",
        )

        self.assertFalse(
            config.exibir
        )

    def test_grupo_padrao_remove_configuracao(self):
        from apps.core.models import ConfiguracaoDashboardGrupo

        ConfiguracaoDashboardGrupo.objects.create(
            grupo=self.grupo,
            modulo="parcerias",
            exibir=False,
        )

        self.client.force_login(self.superuser)

        self.client.post(
            reverse(
                "dashboard_acessos_grupo",
                args=[self.grupo.pk],
            ),
            {
                "dashboard_parcerias": "padrao",
            },
        )

        self.assertFalse(
            ConfiguracaoDashboardGrupo.objects.filter(
                grupo=self.grupo,
                modulo="parcerias",
            ).exists()
        )

    def test_matriz_mostra_acesso_e_dashboard_efetivo(self):
        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse("dashboard_acessos_painel")
        )

        self.assertContains(
            resposta,
            "Acesso",
        )

        self.assertContains(
            resposta,
            "Individual",
        )

        self.assertContains(
            resposta,
            "Grupo",
        )

        self.assertContains(
            resposta,
            "Efetivo",
        )

    def test_dashboard_nunca_exibe_sem_acesso_ao_modulo(self):
        from apps.core.models import ConfiguracaoDashboardUsuario
        from apps.core.dashboard_permissoes import (
            modulos_dashboard_usuario,
        )

        ConfiguracaoDashboardUsuario.objects.create(
            usuario=self.usuario,
            modulo="documentos",
            estado=ConfiguracaoDashboardUsuario.Estado.MOSTRAR,
        )

        resultado = modulos_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "documentos",
            resultado,
        )

class Sprint46185WidgetsDashboardTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="usuario_widgets_46185",
            password="teste123",
        )

        self.grupo = Group.objects.create(
            name="Grupo Widgets 46.18.5",
        )

    def test_sem_configuracao_todos_widgets_permanecem_visiveis(self):
        from apps.core.dashboard_widgets_permissoes import (
            widgets_dashboard_usuario,
        )

        resultado = widgets_dashboard_usuario(
            self.usuario
        )

        self.assertIn(
            "execucao_financeira",
            resultado,
        )

        self.assertIn(
            "situacao_parcerias",
            resultado,
        )

        self.assertIn(
            "progresso_trabalho",
            resultado,
        )

    def test_usuario_pode_ocultar_execucao_financeira(self):
        from apps.core.models import (
            ConfiguracaoDashboardWidgetUsuario,
        )
        from apps.core.dashboard_widgets_permissoes import (
            widgets_dashboard_usuario,
        )

        ConfiguracaoDashboardWidgetUsuario.objects.create(
            usuario=self.usuario,
            widget="execucao_financeira",
            estado=ConfiguracaoDashboardWidgetUsuario.Estado.OCULTAR,
        )

        resultado = widgets_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "execucao_financeira",
            resultado,
        )

    def test_usuario_pode_ocultar_situacao_parcerias(self):
        from apps.core.models import (
            ConfiguracaoDashboardWidgetUsuario,
        )
        from apps.core.dashboard_widgets_permissoes import (
            widgets_dashboard_usuario,
        )

        ConfiguracaoDashboardWidgetUsuario.objects.create(
            usuario=self.usuario,
            widget="situacao_parcerias",
            estado=ConfiguracaoDashboardWidgetUsuario.Estado.OCULTAR,
        )

        resultado = widgets_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "situacao_parcerias",
            resultado,
        )

    def test_usuario_pode_ocultar_progresso_trabalho(self):
        from apps.core.models import (
            ConfiguracaoDashboardWidgetUsuario,
        )
        from apps.core.dashboard_widgets_permissoes import (
            widgets_dashboard_usuario,
        )

        ConfiguracaoDashboardWidgetUsuario.objects.create(
            usuario=self.usuario,
            widget="progresso_trabalho",
            estado=ConfiguracaoDashboardWidgetUsuario.Estado.OCULTAR,
        )

        resultado = widgets_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "progresso_trabalho",
            resultado,
        )

    def test_grupo_pode_ocultar_widget(self):
        from apps.core.models import (
            ConfiguracaoDashboardWidgetGrupo,
        )
        from apps.core.dashboard_widgets_permissoes import (
            widgets_dashboard_usuario,
        )

        self.usuario.groups.add(
            self.grupo
        )

        ConfiguracaoDashboardWidgetGrupo.objects.create(
            grupo=self.grupo,
            widget="progresso_trabalho",
            exibir=False,
        )

        resultado = widgets_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "progresso_trabalho",
            resultado,
        )

    def test_grupo_pode_mostrar_widget(self):
        from apps.core.models import (
            ConfiguracaoDashboardWidgetGrupo,
        )
        from apps.core.dashboard_widgets_permissoes import (
            widgets_dashboard_usuario,
        )

        self.usuario.groups.add(
            self.grupo
        )

        ConfiguracaoDashboardWidgetGrupo.objects.create(
            grupo=self.grupo,
            widget="execucao_financeira",
            exibir=True,
        )

        resultado = widgets_dashboard_usuario(
            self.usuario
        )

        self.assertIn(
            "execucao_financeira",
            resultado,
        )

    def test_individual_ocultar_prevalece_sobre_grupo_mostrar(self):
        from apps.core.models import (
            ConfiguracaoDashboardWidgetGrupo,
            ConfiguracaoDashboardWidgetUsuario,
        )
        from apps.core.dashboard_widgets_permissoes import (
            widgets_dashboard_usuario,
        )

        self.usuario.groups.add(
            self.grupo
        )

        ConfiguracaoDashboardWidgetGrupo.objects.create(
            grupo=self.grupo,
            widget="progresso_trabalho",
            exibir=True,
        )

        ConfiguracaoDashboardWidgetUsuario.objects.create(
            usuario=self.usuario,
            widget="progresso_trabalho",
            estado=ConfiguracaoDashboardWidgetUsuario.Estado.OCULTAR,
        )

        resultado = widgets_dashboard_usuario(
            self.usuario
        )

        self.assertNotIn(
            "progresso_trabalho",
            resultado,
        )

    def test_um_grupo_mostrar_prevalece_sobre_outro_ocultar(self):
        from apps.core.models import (
            ConfiguracaoDashboardWidgetGrupo,
        )
        from apps.core.dashboard_widgets_permissoes import (
            widgets_dashboard_usuario,
        )

        outro_grupo = Group.objects.create(
            name="Outro Grupo Widgets 46.18.5",
        )

        self.usuario.groups.add(
            self.grupo,
            outro_grupo,
        )

        ConfiguracaoDashboardWidgetGrupo.objects.create(
            grupo=self.grupo,
            widget="situacao_parcerias",
            exibir=False,
        )

        ConfiguracaoDashboardWidgetGrupo.objects.create(
            grupo=outro_grupo,
            widget="situacao_parcerias",
            exibir=True,
        )

        resultado = widgets_dashboard_usuario(
            self.usuario
        )

        self.assertIn(
            "situacao_parcerias",
            resultado,
        )

class Sprint46185WidgetsDashboardIntegracaoTests(TestCase):

    def setUp(self):
        from apps.core.models import (
            ConfiguracaoDashboardWidgetUsuario,
        )

        self.ConfiguracaoWidget = (
            ConfiguracaoDashboardWidgetUsuario
        )

        self.usuario = User.objects.create_superuser(
            username="admin_widgets_integracao_46185",
            email="widgets46185@example.com",
            password="teste123",
        )

        self.client.force_login(
            self.usuario
        )

    def _ocultar(self, widget):
        self.ConfiguracaoWidget.objects.create(
            usuario=self.usuario,
            widget=widget,
            estado=self.ConfiguracaoWidget.Estado.OCULTAR,
        )

    def test_ocultar_execucao_financeira_remove_bloco_do_html(self):
        self._ocultar("execucao_financeira")

        resposta = self.client.get(
            reverse("home")
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertNotContains(
            resposta,
            "Visão executiva do escopo",
        )

    def test_ocultar_situacao_parcerias_remove_bloco_do_html(self):
        self._ocultar("situacao_parcerias")

        resposta = self.client.get(
            reverse("home")
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertNotContains(
            resposta,
            "Situação das parcerias",
        )

    def test_ocultar_progresso_trabalho_remove_bloco_do_html(self):
        self._ocultar("progresso_trabalho")

        resposta = self.client.get(
            reverse("home")
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertNotContains(
            resposta,
            "Progresso do trabalho",
        )
