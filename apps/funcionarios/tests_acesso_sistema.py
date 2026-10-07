from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario


class GerenciamentoAcessoSistemaTests(TestCase):
    SENHA = "SenhaSegura!2026Zx"

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="Empresa Teste Acesso"
        )

        self.outra_empresa = Empresa.objects.create(
            nome="Outra Empresa Teste"
        )

        self.operador = User.objects.create_user(
            username="operador_acesso",
            password=self.SENHA,
        )

        self.operador_funcionario = Funcionario.objects.create(
            empresa=self.empresa,
            nome="Operador de Acesso",
            cpf="52998224725",
            user=self.operador,
        )

        self.alvo = Funcionario.objects.create(
            empresa=self.empresa,
            nome="Colaborador Sem Acesso",
            cpf="11144477735",
        )

        self.alvo_outra_empresa = Funcionario.objects.create(
            empresa=self.outra_empresa,
            nome="Colaborador Outra Empresa",
            cpf="12345678909",
        )

        permissoes = Permission.objects.filter(
            content_type__app_label="funcionarios",
            codename__in=[
                "view_funcionario_acesso_sistema",
                "change_funcionario_acesso_sistema",
            ],
        )

        self.operador.user_permissions.add(*permissoes)

        self.client.force_login(self.operador)

    def url(self, funcionario=None):
        funcionario = funcionario or self.alvo

        return reverse(
            "gerenciar_acesso_funcionario",
            kwargs={"pk": funcionario.pk},
        )

    def vincular_usuario_ao_alvo(
        self,
        username="usuario.alvo",
        ativo=True,
    ):
        usuario = User.objects.create_user(
            username=username,
            password=self.SENHA,
        )

        usuario.is_active = ativo
        usuario.save(update_fields=["is_active"])

        Funcionario.objects.filter(
            pk=self.alvo.pk
        ).update(
            user=usuario
        )

        self.alvo.refresh_from_db()

        return usuario

    def test_exibe_formulario_para_colaborador_sem_acesso(self):
        response = self.client.get(self.url())

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Conceder acesso ao PGP",
        )

        self.assertContains(
            response,
            'name="username"',
        )

        self.assertContains(
            response,
            'name="password1"',
        )

        self.assertContains(
            response,
            'name="password2"',
        )

        self.assertIsNone(
            self.alvo.user_id
        )

    def test_concede_acesso_e_vincula_user_ao_colaborador(self):
        response = self.client.post(
            self.url(),
            {
                "acao": "conceder",
                "username": "novo.colaborador",
                "password1": self.SENHA,
                "password2": self.SENHA,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.alvo.refresh_from_db()

        self.assertIsNotNone(
            self.alvo.user_id
        )

        self.assertEqual(
            self.alvo.user.username,
            "novo.colaborador",
        )

        self.assertTrue(
            self.alvo.user.is_active
        )

        self.assertTrue(
            self.alvo.user.check_password(
                self.SENHA
            )
        )

    def test_username_duplicado_nao_vincula_usuario(self):
        User.objects.create_user(
            username="usuario.existente",
            password=self.SENHA,
        )

        response = self.client.post(
            self.url(),
            {
                "acao": "conceder",
                "username": "usuario.existente",
                "password1": self.SENHA,
                "password2": self.SENHA,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.alvo.refresh_from_db()

        self.assertIsNone(
            self.alvo.user_id
        )

        self.assertTrue(
            response.context["acesso_form"].errors
        )

    def test_desativa_acesso_existente(self):
        usuario = self.vincular_usuario_ao_alvo()

        response = self.client.post(
            self.url(),
            {
                "acao": "desativar",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        usuario.refresh_from_db()

        self.assertFalse(
            usuario.is_active
        )

    def test_reativa_acesso_existente(self):
        usuario = self.vincular_usuario_ao_alvo(
            ativo=False
        )

        response = self.client.post(
            self.url(),
            {
                "acao": "ativar",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        usuario.refresh_from_db()

        self.assertTrue(
            usuario.is_active
        )

    def test_nao_permite_desativar_propria_conta(self):
        response = self.client.post(
            self.url(
                self.operador_funcionario
            ),
            {
                "acao": "desativar",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "desativada por esta tela",
        )

        self.operador.refresh_from_db()

        self.assertTrue(
            self.operador.is_active
        )

    def test_nao_acessa_colaborador_de_outra_empresa(self):
        response = self.client.get(
            self.url(
                self.alvo_outra_empresa
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_sem_permissao_nao_acessa_gerenciamento(self):
        self.operador.user_permissions.clear()

        response = self.client.get(
            self.url()
        )

        self.assertEqual(
            response.status_code,
            403,
        )
