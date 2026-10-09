from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.core.testes_documentos import cpf_teste
from apps.documentos.models import Documento
from apps.funcionarios.models import Funcionario
from apps.empresas.models import Empresa


class DocumentoAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Documentos")
        cls.documento = Documento.objects.create(
            descricao="Nota fiscal de teste",
            arquivo=SimpleUploadedFile(
                "nota.pdf",
                b"conteudo de teste",
                content_type="application/pdf",
            ),
            empresa=cls.empresa,
        )
        cls.user = User.objects.create_user(
            username="documento_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        self.assertEqual(
            self.client.get(reverse("list_documentos")).status_code,
            302,
        )

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("list_documentos")).status_code,
            403,
        )

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_documento",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("list_documentos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nota fiscal de teste")

    def test_percentual_conferencia(self):
        self.documento.documento_legivel = True
        self.documento.dados_compativeis = True
        self.assertEqual(self.documento.percentual_conferencia, 40)

class DocumentoEscopoMultiempresaTests(TestCase):

    def setUp(self):
        UserModel = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="Empresa Documento A",
        )
        self.empresa_b = Empresa.objects.create(
            nome="Empresa Documento B",
        )

        self.documento_a = Documento.objects.create(
            descricao="Documento empresa A",
            arquivo=SimpleUploadedFile(
                "doc-a.pdf",
                b"conteudo-a",
                content_type="application/pdf",
            ),
            empresa=self.empresa_a,
        )

        self.documento_b = Documento.objects.create(
            descricao="Documento empresa B",
            arquivo=SimpleUploadedFile(
                "doc-b.pdf",
                b"conteudo-b",
                content_type="application/pdf",
            ),
            empresa=self.empresa_b,
        )

        self.permissao = Permission.objects.get(
            content_type__app_label="documentos",
            codename="view_documento",
        )

        self.usuario_a = UserModel.objects.create_user(
            username="doc_escopo_a",
            password="teste12345",
        )
        self.usuario_a.user_permissions.add(
            self.permissao
        )

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Usuario Documento A",
            usuario="doc_escopo_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="doc-a@example.test",
            Telefone="-",
            user=self.usuario_a,
            empresa=self.empresa_a,
            imagem="funcionarios_photos/teste.jpg",
        )

        self.staff_a = UserModel.objects.create_user(
            username="doc_staff_a",
            password="teste12345",
            is_staff=True,
        )
        self.staff_a.user_permissions.add(
            self.permissao
        )

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Staff Documento A",
            usuario="doc_staff_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="doc-staff-a@example.test",
            Telefone="-",
            user=self.staff_a,
            empresa=self.empresa_a,
            imagem="funcionarios_photos/teste.jpg",
        )

        self.usuario_b = UserModel.objects.create_user(
            username="doc_escopo_b",
            password="teste12345",
        )
        self.usuario_b.user_permissions.add(
            self.permissao
        )

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Usuario Documento B",
            usuario="doc_escopo_b",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="doc-b@example.test",
            Telefone="-",
            user=self.usuario_b,
            empresa=self.empresa_b,
            imagem="funcionarios_photos/teste.jpg",
        )

        self.usuario_sem_empresa = UserModel.objects.create_user(
            username="doc_sem_empresa",
            password="teste12345",
        )
        self.usuario_sem_empresa.user_permissions.add(
            self.permissao
        )

        self.gestor = UserModel.objects.create_user(
            username="doc_gestor",
            password="teste12345",
        )
        self.gestor.user_permissions.add(
            self.permissao
        )

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal"
        )
        self.gestor.groups.add(grupo)

    def test_usuario_empresa_a_ve_apenas_documentos_da_empresa_a(self):
        self.client.force_login(self.usuario_a)

        response = self.client.get(
            reverse("list_documentos")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        ids = {
            obj.pk
            for obj in response.context["documentos"]
        }

        self.assertEqual(
            ids,
            {self.documento_a.pk},
        )

    def test_staff_comum_nao_ganha_visao_global(self):
        self.client.force_login(self.staff_a)

        response = self.client.get(
            reverse("list_documentos")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        ids = {
            obj.pk
            for obj in response.context["documentos"]
        }

        self.assertEqual(
            ids,
            {self.documento_a.pk},
        )

    def test_empresa_b_nao_acessa_detalhe_da_empresa_a(self):
        self.client.force_login(self.usuario_b)

        response = self.client.get(
            reverse(
                "detail_documento",
                kwargs={"pk": self.documento_a.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_usuario_sem_empresa_nao_recebe_documentos(self):
        self.client.force_login(
            self.usuario_sem_empresa
        )

        response = self.client.get(
            reverse("list_documentos")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["documentos"]),
            [],
        )

    def test_gestor_municipal_recebe_visao_global(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("list_documentos")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        ids = {
            obj.pk
            for obj in response.context["documentos"]
        }

        self.assertEqual(
            ids,
            {
                self.documento_a.pk,
                self.documento_b.pk,
            },
        )
