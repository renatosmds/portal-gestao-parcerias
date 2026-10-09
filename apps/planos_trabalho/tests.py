from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.planos_trabalho.models import PlanoTrabalho
from apps.termos.models import Termos


class PlanosTrabalhoEscopoPermissaoTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="OSC A Planos",
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC B Planos",
        )

        self.usuario_a = User.objects.create_user(
            username="staff_plano_a",
            password="teste12345",
            is_staff=True,
        )

        self.usuario_b = User.objects.create_user(
            username="staff_plano_b",
            password="teste12345",
            is_staff=True,
        )

        self.usuario_sem_empresa = User.objects.create_user(
            username="staff_plano_sem_empresa",
            password="teste12345",
            is_staff=True,
        )

        self.usuario_inativo = User.objects.create_user(
            username="staff_plano_inativo",
            password="teste12345",
            is_staff=True,
        )

        self.usuario_sem_permissao = User.objects.create_user(
            username="usuario_sem_plano",
            password="teste12345",
        )

        self.superusuario = User.objects.create_superuser(
            username="admin_plano_global",
            email="admin-plano@example.test",
            password="teste12345",
        )

        Funcionario.objects.create(
            cpf="52998224725",
            nome="Staff Plano A",
            usuario="staff_plano_a",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="staff_plano_a@example.test",
            Telefone="000000000",
            user=self.usuario_a,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
        )

        Funcionario.objects.create(
            cpf="16899535009",
            nome="Staff Plano B",
            usuario="staff_plano_b",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="staff_plano_b@example.test",
            Telefone="000000000",
            user=self.usuario_b,
            empresa=self.empresa_b,
            imagem="funcionarios/teste.jpg",
        )

        Funcionario.objects.create(
            cpf="11144477735",
            nome="Staff Plano Inativo",
            usuario="staff_plano_inativo",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="staff_plano_inativo@example.test",
            Telefone="000000000",
            user=self.usuario_inativo,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
            ativo=False,
        )

        self.permissao = Permission.objects.get(
            content_type__app_label="planos_trabalho",
            codename="view_planotrabalho",
        )

        for usuario in (
            self.usuario_a,
            self.usuario_b,
            self.usuario_sem_empresa,
            self.usuario_inativo,
        ):
            usuario.user_permissions.add(
                self.permissao
            )

        self.termo_a = Termos.objects.create(
            numtermo="PT-A",
            termo="Termo A",
            empresa=self.empresa_a,
        )

        self.termo_b = Termos.objects.create(
            numtermo="PT-B",
            termo="Termo B",
            empresa=self.empresa_b,
        )

        self.plano_a = PlanoTrabalho.objects.create(
            termo=self.termo_a,
            versao=1,
            titulo="Plano A",
        )

        self.plano_b = PlanoTrabalho.objects.create(
            termo=self.termo_b,
            versao=1,
            titulo="Plano B",
        )

    def test_sem_permissao_do_modulo_recebe_403(self):
        self.client.force_login(
            self.usuario_sem_permissao
        )

        response = self.client.get(
            reverse("planos_trabalho:plano_lista")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_empresa_a_ve_apenas_plano_da_empresa_a(self):
        self.client.force_login(
            self.usuario_a
        )

        response = self.client.get(
            reverse("planos_trabalho:plano_lista")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["planos"]),
            [self.plano_a],
        )

    def test_empresa_b_nao_acessa_plano_da_empresa_a(self):
        self.client.force_login(
            self.usuario_b
        )

        response = self.client.get(
            reverse(
                "planos_trabalho:plano_detalhe",
                args=[self.plano_a.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_staff_sem_empresa_nao_recebe_planos(self):
        self.client.force_login(
            self.usuario_sem_empresa
        )

        response = self.client.get(
            reverse("planos_trabalho:plano_lista")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["planos"]),
            [],
        )

    def test_funcionario_inativo_nao_recebe_planos(self):
        self.client.force_login(
            self.usuario_inativo
        )

        response = self.client.get(
            reverse("planos_trabalho:plano_lista")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["planos"]),
            [],
        )

    def test_superusuario_recebe_visao_global(self):
        self.client.force_login(
            self.superusuario
        )

        response = self.client.get(
            reverse("planos_trabalho:plano_lista")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        ids = {
            plano.pk
            for plano in response.context["planos"]
        }

        self.assertEqual(
            ids,
            {
                self.plano_a.pk,
                self.plano_b.pk,
            },
        )
