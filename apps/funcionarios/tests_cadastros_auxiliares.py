from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from apps.departamentos.models import Departamento
from apps.empresas.models import Empresa

from .forms import FuncionarioForm
from .models import Cargo, Funcionario


class CadastrosAuxiliaresTests(TestCase):

    def setUp(self):
        self.empresa1 = Empresa.objects.create(
            nome="Empresa A",
        )
        self.empresa2 = Empresa.objects.create(
            nome="Empresa B",
        )

        self.user = User.objects.create_user(
            username="gestor_cadastros",
            password="teste123",
        )

        self.funcionario = Funcionario.objects.create(
            nome="Gestor Teste",
            cpf="11144477735",
            empresa=self.empresa1,
            user=self.user,
        )

        self.cargo1 = Cargo.objects.create(
            empresa=self.empresa1,
            nome="Cargo Teste A",
        )

        self.cargo2 = Cargo.objects.create(
            empresa=self.empresa2,
            nome="Cargo Teste B",
        )

        self.unidade1 = Departamento.objects.create(
            empresa=self.empresa1,
            nome="Unidade Teste A",
        )

        self.unidade2 = Departamento.objects.create(
            empresa=self.empresa2,
            nome="Unidade Teste B",
        )

    def conceder(self, *codenames):
        permissoes = Permission.objects.filter(
            content_type__app_label="funcionarios",
            codename__in=codenames,
        )
        self.user.user_permissions.add(
            *permissoes
        )

    def test_lotacao_filtrada_por_empresa(self):
        self.conceder(
            "view_funcionario_identificacao",
            "change_funcionario_identificacao",
        )

        form = FuncionarioForm(
            user=self.user,
            instance=self.funcionario,
        )

        self.assertIn(
            self.unidade1,
            form.fields[
                "departamentos"
            ].queryset,
        )

        self.assertNotIn(
            self.unidade2,
            form.fields[
                "departamentos"
            ].queryset,
        )

    def test_lista_cargos_respeita_empresa(self):
        self.conceder(
            "view_cargo",
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "list_cargos"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Cargo Teste A",
        )

        self.assertNotContains(
            response,
            "Cargo Teste B",
        )

    def test_cria_cargo_na_empresa_usuario(self):
        self.conceder(
            "view_cargo",
            "add_cargo",
        )

        self.client.force_login(
            self.user
        )

        response = self.client.post(
            reverse(
                "create_cargo"
            ),
            {
                "nome": "Cargo Novo",
                "descricao": "",
                "ativo": "on",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            Cargo.objects.filter(
                empresa=self.empresa1,
                nome="Cargo Novo",
            ).exists()
        )

    def test_nao_edita_cargo_de_outra_empresa(self):
        self.conceder(
            "change_cargo",
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "update_cargo",
                kwargs={
                    "pk": self.cargo2.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_nao_exclui_cargo_de_outra_empresa(self):
        self.conceder(
            "delete_cargo",
        )

        self.client.force_login(
            self.user
        )

        response = self.client.get(
            reverse(
                "delete_cargo",
                kwargs={
                    "pk": self.cargo2.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_usuario_sem_empresa_nao_acessa_cadastros(self):
        usuario_sem_empresa = User.objects.create_user(
            username="sem_empresa",
            password="teste123",
        )

        permissao = Permission.objects.get(
            content_type__app_label="funcionarios",
            codename="view_cargo",
        )

        usuario_sem_empresa.user_permissions.add(
            permissao
        )

        self.client.force_login(
            usuario_sem_empresa
        )

        response = self.client.get(
            reverse(
                "list_cargos"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_superuser_lista_apenas_empresa_selecionada(self):
        admin = User.objects.create_superuser(
            username="admin_cadastros",
            email="admin@example.com",
            password="senha-teste-123",
        )

        self.client.force_login(admin)

        response = self.client.get(
            reverse("list_cargos"),
            {
                "empresa": self.empresa1.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Cargo Teste A",
        )

        self.assertNotContains(
            response,
            "Cargo Teste B",
        )

    def test_relacionamento_lotacao(self):
        self.funcionario.departamentos.add(
            self.unidade1
        )

        self.assertTrue(
            self.funcionario.departamentos.filter(
                pk=self.unidade1.pk
            ).exists()
        )
