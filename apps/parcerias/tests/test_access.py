from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from apps.core.testes_documentos import cpf_teste
from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.parcerias.models import Parcerias


class ParceriaAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Parceria")
        cls.parceria = Parcerias.objects.create(
            nomeOSC="OSC Teste",
            empresa=cls.empresa,
        )
        cls.user = User.objects.create_user(
            username="parceria_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        response = self.client.get(reverse("list_parcerias"))
        self.assertEqual(response.status_code, 302)

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("list_parcerias"))
        self.assertEqual(response.status_code, 403)

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_parceria",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("list_parcerias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OSC Teste")

    def test_superuser_abre_detalhe(self):
        admin = User.objects.create_superuser(
            username="admin_detalhe_parceria",
            email="admin2@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(
            reverse("detail_parceria", kwargs={"pk": self.parceria.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OSC Teste")


class ParceriaEscopoMultiempresaTests(TestCase):

    def setUp(self):
        UserModel = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="OSC A Parcerias",
        )
        self.empresa_b = Empresa.objects.create(
            nome="OSC B Parcerias",
        )

        self.parceria_a = Parcerias.objects.create(
            nomeOSC="Parceria Empresa A",
            empresa=self.empresa_a,
        )
        self.parceria_b = Parcerias.objects.create(
            nomeOSC="Parceria Empresa B",
            empresa=self.empresa_b,
        )

        permissoes = Permission.objects.filter(
            content_type__app_label="parcerias",
        )

        self.usuario_a = UserModel.objects.create_user(
            username="parceria_a",
            password="teste12345",
        )
        self.usuario_a.user_permissions.add(*permissoes)

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Usuario Parceria A",
            usuario="parceria_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="parceria-a@example.test",
            Telefone="-",
            user=self.usuario_a,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
        )

        self.staff_a = UserModel.objects.create_user(
            username="parceria_staff_a",
            password="teste12345",
            is_staff=True,
        )
        self.staff_a.user_permissions.add(*permissoes)

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Staff Parceria A",
            usuario="parceria_staff_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="parceria-staff-a@example.test",
            Telefone="-",
            user=self.staff_a,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
        )

        self.usuario_b = UserModel.objects.create_user(
            username="parceria_b",
            password="teste12345",
        )
        self.usuario_b.user_permissions.add(*permissoes)

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Usuario Parceria B",
            usuario="parceria_b",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="parceria-b@example.test",
            Telefone="-",
            user=self.usuario_b,
            empresa=self.empresa_b,
            imagem="funcionarios/teste.jpg",
        )

        self.usuario_sem_empresa = UserModel.objects.create_user(
            username="parceria_sem_empresa",
            password="teste12345",
        )
        self.usuario_sem_empresa.user_permissions.add(
            *permissoes
        )

        self.gestor = UserModel.objects.create_user(
            username="parceria_gestor",
            password="teste12345",
        )
        self.gestor.user_permissions.add(*permissoes)

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal",
        )
        self.gestor.groups.add(grupo)

    def test_usuario_empresa_a_ve_apenas_parceria_a(self):
        self.client.force_login(self.usuario_a)

        response = self.client.get(
            reverse("list_parcerias")
        )

        self.assertEqual(response.status_code, 200)

        ids = {
            item.pk
            for item in response.context["parcerias"]
        }

        self.assertEqual(
            ids,
            {self.parceria_a.pk},
        )

    def test_staff_comum_nao_ganha_visao_global(self):
        self.client.force_login(self.staff_a)

        response = self.client.get(
            reverse("list_parcerias")
        )

        self.assertEqual(response.status_code, 200)

        ids = {
            item.pk
            for item in response.context["parcerias"]
        }

        self.assertEqual(
            ids,
            {self.parceria_a.pk},
        )

    def test_empresa_b_nao_acessa_detalhe_da_empresa_a(self):
        self.client.force_login(self.usuario_b)

        response = self.client.get(
            reverse(
                "detail_parceria",
                kwargs={"pk": self.parceria_a.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_usuario_sem_empresa_nao_recebe_parcerias(self):
        self.client.force_login(
            self.usuario_sem_empresa
        )

        response = self.client.get(
            reverse("list_parcerias")
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            list(response.context["parcerias"]),
            [],
        )

    def test_gestor_municipal_recebe_visao_global(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("list_parcerias")
        )

        self.assertEqual(response.status_code, 200)

        ids = {
            item.pk
            for item in response.context["parcerias"]
        }

        self.assertEqual(
            ids,
            {
                self.parceria_a.pk,
                self.parceria_b.pk,
            },
        )
