from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class Sprint4617AdministracaoAcessosTests(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin4617",
            email="admin4617@example.com",
            password="teste123",
        )

        self.staff = User.objects.create_user(
            username="staff4617",
            password="teste123",
            is_staff=True,
        )

        self.usuario = User.objects.create_user(
            username="usuario4617",
            password="teste123",
        )

    def test_acessos_exige_login(self):
        resposta = self.client.get(
            reverse("acessos_painel")
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

    def test_usuario_comum_nao_acessa(self):
        self.client.force_login(
            self.usuario
        )

        resposta = self.client.get(
            reverse("acessos_painel")
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

    def test_staff_nao_superusuario_nao_acessa(self):
        self.client.force_login(
            self.staff
        )

        resposta = self.client.get(
            reverse("acessos_painel")
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

    def test_superusuario_acessa_painel(self):
        self.client.force_login(
            self.superuser
        )

        resposta = self.client.get(
            reverse("acessos_painel")
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

    def test_superusuario_pode_editar_acessos_usuario(self):
        self.client.force_login(
            self.superuser
        )

        permissao = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        resposta = self.client.post(
            reverse(
                "acessos_usuario",
                args=[self.usuario.pk],
            ),
            {
                "modulos": [
                    "parcerias",
                ],
            },
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertTrue(
            self.usuario.user_permissions.filter(
                pk=permissao.pk
            ).exists()
        )

    def test_superusuario_pode_editar_acessos_grupo(self):
        self.client.force_login(
            self.superuser
        )

        grupo = Group.objects.create(
            name="Analistas 46.17",
        )

        permissao = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        resposta = self.client.post(
            reverse(
                "acessos_grupo",
                args=[grupo.pk],
            ),
            {
                "modulos": [
                    "parcerias",
                ],
            },
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertTrue(
            grupo.permissions.filter(
                pk=permissao.pk
            ).exists()
        )

    def test_matriz_identifica_permissao_direta(self):
        permissao = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        self.usuario.user_permissions.add(
            permissao
        )

        self.client.force_login(
            self.superuser
        )

        resposta = self.client.get(
            reverse("acessos_painel")
        )

        self.assertContains(
            resposta,
            'data-direto="sim"',
        )

    def test_matriz_identifica_permissao_por_grupo(self):
        grupo = Group.objects.create(
            name="Grupo Parcerias 46.17",
        )

        permissao = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        grupo.permissions.add(
            permissao
        )

        self.usuario.groups.add(
            grupo
        )

        self.client.force_login(
            self.superuser
        )

        resposta = self.client.get(
            reverse("acessos_painel")
        )

        self.assertContains(
            resposta,
            "Grupo",
        )

class Sprint4617SegurancaAcessosTests(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_seg_4617",
            email="admin_seg_4617@example.com",
            password="teste123",
        )

        self.staff = User.objects.create_user(
            username="staff_seg_4617",
            password="teste123",
            is_staff=True,
        )

        self.usuario = User.objects.create_user(
            username="usuario_seg_4617",
            password="teste123",
        )

        self.grupo = Group.objects.create(
            name="Grupo Segurança 46.17",
        )

    def test_edicao_usuario_preserva_permissao_nao_controlada(self):
        self.client.force_login(self.superuser)

        permissao_extra = Permission.objects.exclude(
            content_type__app_label__in=[
                codigo.split(".", 1)[0]
                for permissoes in __import__(
                    "apps.core.permissoes_modulos",
                    fromlist=["MODULOS"],
                ).MODULOS.values()
                for codigo in permissoes
            ]
        ).first()

        self.assertIsNotNone(permissao_extra)

        self.usuario.user_permissions.add(
            permissao_extra
        )

        self.client.post(
            reverse(
                "acessos_usuario",
                args=[self.usuario.pk],
            ),
            {
                "modulos": ["parcerias"],
            },
        )

        self.assertTrue(
            self.usuario.user_permissions.filter(
                pk=permissao_extra.pk
            ).exists()
        )

    def test_staff_nao_acessa_edicao_de_usuario(self):
        self.client.force_login(self.staff)

        resposta = self.client.get(
            reverse(
                "acessos_usuario",
                args=[self.usuario.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

    def test_staff_nao_acessa_edicao_de_grupo(self):
        self.client.force_login(self.staff)

        resposta = self.client.get(
            reverse(
                "acessos_grupo",
                args=[self.grupo.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

    def test_relatorios_nao_aparece_como_checkbox_usuario(self):
        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse(
                "acessos_usuario",
                args=[self.usuario.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertNotContains(
            resposta,
            'value="relatorios"',
        )

    def test_relatorios_nao_aparece_como_checkbox_grupo(self):
        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse(
                "acessos_grupo",
                args=[self.grupo.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertNotContains(
            resposta,
            'value="relatorios"',
        )

    def test_post_relatorios_nao_concede_permissoes_indiretas(self):
        self.client.force_login(self.superuser)

        self.client.post(
            reverse(
                "acessos_usuario",
                args=[self.usuario.pk],
            ),
            {
                "modulos": ["relatorios"],
            },
        )

        self.usuario.refresh_from_db()

        self.assertFalse(
            self.usuario.has_perm(
                "diligencias.view_diligencia"
            )
        )

        self.assertFalse(
            self.usuario.has_perm(
                "lancamentos.view_lancamento"
            )
        )

        self.assertFalse(
            self.usuario.has_perm(
                "funcionarios.view_funcionario"
            )
        )

        self.assertFalse(
            self.usuario.has_perm(
                "funcionarios.view_folhapagamento"
            )
        )

class Sprint4617InterfaceAcessosTests(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_ui_4617",
            email="admin_ui_4617@example.com",
            password="teste123",
        )

        self.usuario = User.objects.create_user(
            username="usuario_ui_4617",
            password="teste123",
        )

    def test_superusuario_ve_link_administracao_acessos(self):
        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse("home")
        )

        self.assertContains(
            resposta,
            "Administração de Acessos",
        )

        self.assertContains(
            resposta,
            reverse("acessos_painel"),
        )

    def test_usuario_comum_nao_ve_link_administracao_acessos(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(
            reverse("home")
        )

        self.assertNotContains(
            resposta,
            "Administração de Acessos",
        )

    def test_superusuario_pode_criar_grupo_pela_interface(self):
        self.client.force_login(self.superuser)

        resposta = self.client.post(
            reverse("acessos_grupo_novo"),
            {
                "nome": "Analistas de Prestação",
            },
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertTrue(
            Group.objects.filter(
                name="Analistas de Prestação",
            ).exists()
        )

    def test_usuario_comum_nao_pode_criar_grupo(self):
        self.client.force_login(self.usuario)

        resposta = self.client.post(
            reverse("acessos_grupo_novo"),
            {
                "nome": "Grupo Indevido",
            },
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

        self.assertFalse(
            Group.objects.filter(
                name="Grupo Indevido",
            ).exists()
        )

class Sprint4617GruposUsuarioMatrizTests(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_grupos_4617",
            email="admin_grupos_4617@example.com",
            password="teste123",
        )

        self.usuario = User.objects.create_user(
            username="usuario_grupos_4617",
            password="teste123",
        )

        self.grupo_a = Group.objects.create(
            name="Analistas 46.17",
        )

        self.grupo_b = Group.objects.create(
            name="Gestores 46.17",
        )

    def test_superusuario_pode_vincular_usuario_a_grupos(self):
        self.client.force_login(self.superuser)

        resposta = self.client.post(
            reverse(
                "acessos_usuario_grupos",
                args=[self.usuario.pk],
            ),
            {
                "grupos": [
                    str(self.grupo_a.pk),
                    str(self.grupo_b.pk),
                ],
            },
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            set(
                self.usuario.groups.values_list(
                    "pk",
                    flat=True,
                )
            ),
            {
                self.grupo_a.pk,
                self.grupo_b.pk,
            },
        )

    def test_superusuario_pode_remover_grupo_do_usuario(self):
        self.usuario.groups.add(
            self.grupo_a,
            self.grupo_b,
        )

        self.client.force_login(self.superuser)

        self.client.post(
            reverse(
                "acessos_usuario_grupos",
                args=[self.usuario.pk],
            ),
            {
                "grupos": [
                    str(self.grupo_b.pk),
                ],
            },
        )

        self.assertEqual(
            list(
                self.usuario.groups.values_list(
                    "pk",
                    flat=True,
                )
            ),
            [self.grupo_b.pk],
        )

    def test_usuario_comum_nao_pode_alterar_grupos(self):
        atacante = User.objects.create_user(
            username="atacante_4617",
            password="teste123",
        )

        self.client.force_login(atacante)

        resposta = self.client.post(
            reverse(
                "acessos_usuario_grupos",
                args=[self.usuario.pk],
            ),
            {
                "grupos": [
                    str(self.grupo_a.pk),
                ],
            },
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

        self.assertFalse(
            self.usuario.groups.exists()
        )

    def test_matriz_expoe_colunas_direto_grupo_efetivo(self):
        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse("acessos_painel")
        )

        self.assertContains(
            resposta,
            "Direto",
        )

        self.assertContains(
            resposta,
            "Grupo",
        )

        self.assertContains(
            resposta,
            "Efetivo",
        )

    def test_matriz_mostra_acesso_direto(self):
        permissao = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        self.usuario.user_permissions.add(
            permissao
        )

        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse("acessos_painel")
        )

        self.assertContains(
            resposta,
            'data-usuario="usuario_grupos_4617"',
        )

        self.assertContains(
            resposta,
            'data-modulo="parcerias"',
        )

        self.assertContains(
            resposta,
            'data-direto="sim"',
        )

        self.assertContains(
            resposta,
            'data-efetivo="sim"',
        )

    def test_matriz_mostra_acesso_por_grupo(self):
        permissao = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        self.grupo_a.permissions.add(
            permissao
        )

        self.usuario.groups.add(
            self.grupo_a
        )

        self.client.force_login(self.superuser)

        resposta = self.client.get(
            reverse("acessos_painel")
        )

        self.assertContains(
            resposta,
            'data-grupo="sim"',
        )

        self.assertContains(
            resposta,
            'data-efetivo="sim"',
        )

class Sprint4617SegurancaFinalTests(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_final_4617",
            email="admin_final_4617@example.com",
            password="teste123",
        )

        self.usuario = User.objects.create_user(
            username="usuario_final_4617",
            password="teste123",
        )

        self.grupo = Group.objects.create(
            name="Grupo Final 46.17",
        )

    def test_id_grupo_inexistente_nao_e_associado(self):
        self.client.force_login(self.superuser)

        self.client.post(
            reverse(
                "acessos_usuario_grupos",
                args=[self.usuario.pk],
            ),
            {
                "grupos": [
                    str(self.grupo.pk),
                    "999999",
                ],
            },
        )

        self.assertEqual(
            list(
                self.usuario.groups.values_list(
                    "pk",
                    flat=True,
                )
            ),
            [self.grupo.pk],
        )

    def test_permissao_por_grupo_reflete_no_acesso_efetivo(self):
        permissao = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )

        self.grupo.permissions.add(
            permissao
        )

        self.usuario.groups.add(
            self.grupo
        )

        self.assertTrue(
            self.usuario.has_perm(
                "parcerias.view_parcerias"
            )
        )

    def test_edicao_de_modulos_nao_remove_superuser(self):
        self.client.force_login(self.superuser)

        self.client.post(
            reverse(
                "acessos_usuario",
                args=[self.superuser.pk],
            ),
            {
                "modulos": [],
            },
        )

        self.superuser.refresh_from_db()

        self.assertTrue(
            self.superuser.is_superuser
        )

        self.assertTrue(
            self.superuser.is_staff
        )
