from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.pareceres.models import ParecerTecnico
from apps.prestacao.models import Prestacao


class PareceresEscopoPermissaoTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="OSC A Pareceres",
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC B Pareceres",
        )

        self.usuario_a = User.objects.create_user(
            username="staff_parecer_a",
            password="teste12345",
            is_staff=True,
        )

        self.usuario_b = User.objects.create_user(
            username="staff_parecer_b",
            password="teste12345",
            is_staff=True,
        )

        self.usuario_sem_empresa = User.objects.create_user(
            username="staff_parecer_sem_empresa",
            password="teste12345",
            is_staff=True,
        )

        self.usuario_inativo = User.objects.create_user(
            username="staff_parecer_inativo",
            password="teste12345",
            is_staff=True,
        )

        self.usuario_sem_permissao = User.objects.create_user(
            username="usuario_sem_parecer",
            password="teste12345",
        )

        self.superusuario = User.objects.create_superuser(
            username="admin_parecer_global",
            email="admin-parecer@example.test",
            password="teste12345",
        )

        Funcionario.objects.create(
            cpf="52998224725",
            nome="Staff Parecer A",
            usuario="staff_parecer_a",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="staff_parecer_a@example.test",
            Telefone="000000000",
            user=self.usuario_a,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
        )

        Funcionario.objects.create(
            cpf="16899535009",
            nome="Staff Parecer B",
            usuario="staff_parecer_b",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="staff_parecer_b@example.test",
            Telefone="000000000",
            user=self.usuario_b,
            empresa=self.empresa_b,
            imagem="funcionarios/teste.jpg",
        )

        Funcionario.objects.create(
            cpf="11144477735",
            nome="Staff Parecer Inativo",
            usuario="staff_parecer_inativo",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="staff_parecer_inativo@example.test",
            Telefone="000000000",
            user=self.usuario_inativo,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
            ativo=False,
        )

        self.permissao = Permission.objects.get(
            content_type__app_label="pareceres",
            codename="view_parecertecnico",
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

        self.prestacao_a = Prestacao.objects.create(
            tipo="cnpj",
            numtermo="PA-001",
            empresa=self.empresa_a,
        )

        self.prestacao_b = Prestacao.objects.create(
            tipo="cnpj",
            numtermo="PB-001",
            empresa=self.empresa_b,
        )

        self.parecer_a = ParecerTecnico.objects.create(
            prestacao=self.prestacao_a,
            empresa=self.empresa_a,
            numero="PARECER-A",
            elaborado_por=self.superusuario,
        )

        self.parecer_b = ParecerTecnico.objects.create(
            prestacao=self.prestacao_b,
            empresa=self.empresa_b,
            numero="PARECER-B",
            elaborado_por=self.superusuario,
        )

    def test_sem_permissao_do_modulo_recebe_403(self):
        self.client.force_login(
            self.usuario_sem_permissao
        )

        response = self.client.get(
            reverse("pareceres:parecer_lista")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_empresa_a_ve_apenas_parecer_da_empresa_a(self):
        self.client.force_login(
            self.usuario_a
        )

        response = self.client.get(
            reverse("pareceres:parecer_lista")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["pareceres"]),
            [self.parecer_a],
        )

    def test_empresa_b_nao_acessa_parecer_da_empresa_a(self):
        self.client.force_login(
            self.usuario_b
        )

        response = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer_a.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_staff_sem_empresa_nao_recebe_pareceres(self):
        self.client.force_login(
            self.usuario_sem_empresa
        )

        response = self.client.get(
            reverse("pareceres:parecer_lista")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["pareceres"]),
            [],
        )

    def test_funcionario_inativo_nao_recebe_pareceres(self):
        self.client.force_login(
            self.usuario_inativo
        )

        response = self.client.get(
            reverse("pareceres:parecer_lista")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["pareceres"]),
            [],
        )

    def test_superusuario_recebe_visao_global(self):
        self.client.force_login(
            self.superusuario
        )

        response = self.client.get(
            reverse("pareceres:parecer_lista")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        ids = {
            parecer.pk
            for parecer in response.context["pareceres"]
        }

        self.assertEqual(
            ids,
            {
                self.parecer_a.pk,
                self.parecer_b.pk,
            },
        )


class ParecerGestorMunicipalTests(TestCase):

    def setUp(self):
        from django.contrib.auth.models import Group

        User = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="OSC A Parecer Gestor",
        )
        self.empresa_b = Empresa.objects.create(
            nome="OSC B Parecer Gestor",
        )

        self.prestacao_a = Prestacao.objects.create(
            tipo="cnpj",
            numtermo="GESTOR-PA",
            empresa=self.empresa_a,
        )

        self.prestacao_b = Prestacao.objects.create(
            tipo="cnpj",
            numtermo="GESTOR-PB",
            empresa=self.empresa_b,
        )

        self.criador = User.objects.create_superuser(
            username="admin_parecer_gestor_fixture",
            email="admin-parecer-gestor@example.test",
            password="teste12345",
        )

        self.parecer_a = ParecerTecnico.objects.create(
            prestacao=self.prestacao_a,
            empresa=self.empresa_a,
            numero="GESTOR-PARECER-A",
            elaborado_por=self.criador,
        )

        self.parecer_b = ParecerTecnico.objects.create(
            prestacao=self.prestacao_b,
            empresa=self.empresa_b,
            numero="GESTOR-PARECER-B",
            elaborado_por=self.criador,
        )

        self.gestor = User.objects.create_user(
            username="gestor_parecer_global",
            password="teste12345",
        )

        permissoes = Permission.objects.filter(
            content_type__app_label="pareceres",
        )
        self.gestor.user_permissions.add(*permissoes)

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal",
        )
        self.gestor.groups.add(grupo)

    def test_gestor_municipal_recebe_visao_global(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("pareceres:parecer_lista")
        )

        self.assertEqual(response.status_code, 200)

        ids = {
            item.pk
            for item in response.context["pareceres"]
        }

        self.assertEqual(
            ids,
            {
                self.parecer_a.pk,
                self.parecer_b.pk,
            },
        )
