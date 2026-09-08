from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.prestacao.models import Prestacao


class PrestacaoAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Prestação")
        cls.prestacao = Prestacao.objects.create(
            numtermo="TC 001/2026",
            credor="OSC Teste",
            tipo="cnpj",
            empresa=cls.empresa,
        )
        cls.user = User.objects.create_user(
            username="prestacao_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        self.assertEqual(
            self.client.get(reverse("list_prestacao")).status_code,
            302,
        )

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("list_prestacao")).status_code,
            403,
        )

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_prestacao",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("list_prestacao"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TC 001/2026")

    def test_str_nunca_retorna_none(self):
        item = Prestacao.objects.create(tipo="cnpj", empresa=self.empresa)
        self.assertEqual(str(item), f"Prestação #{item.pk}")

class PrestacaoIsolamentoEmpresaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(
            nome="Empresa A Prestacao"
        )
        cls.empresa_b = Empresa.objects.create(
            nome="Empresa B Prestacao"
        )

        cls.prestacao_a = Prestacao.objects.create(
            numtermo="PA-001/2026",
            credor="OSC A",
            tipo="cnpj",
            empresa=cls.empresa_a,
        )
        cls.prestacao_b = Prestacao.objects.create(
            numtermo="PB-001/2026",
            credor="OSC B",
            tipo="cnpj",
            empresa=cls.empresa_b,
        )

        cls.user = User.objects.create_user(
            username="prestacao_empresa_a",
            password="teste123",
        )

        permissoes = Permission.objects.filter(
            codename__in=[
                "view_prestacao",
                "change_prestacao",
                "delete_prestacao",
            ]
        )
        cls.user.user_permissions.add(*permissoes)

        Funcionario.objects.create(
            nome="Usuario Prestacao Empresa A",
            usuario="prestacao_empresa_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="-",
            estado="MG",
            email="prestacao-a@example.com",
            Telefone="-",
            user=cls.user,
            empresa=cls.empresa_a,
            imagem="funcionarios_photos/teste.jpg",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_lista_nao_exibe_prestacao_de_outra_empresa(self):
        response = self.client.get(
            reverse("list_prestacao")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PA-001/2026")
        self.assertNotContains(response, "PB-001/2026")

    def test_detalhe_de_outra_empresa_retorna_404(self):
        response = self.client.get(
            reverse(
                "detail_prestacao",
                kwargs={"pk": self.prestacao_b.pk},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_edicao_de_outra_empresa_retorna_404(self):
        response = self.client.get(
            reverse(
                "update_prestacao",
                kwargs={"pk": self.prestacao_b.pk},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_exclusao_de_outra_empresa_retorna_404(self):
        response = self.client.get(
            reverse(
                "delete_prestacao",
                kwargs={"pk": self.prestacao_b.pk},
            )
        )
        self.assertEqual(response.status_code, 404)
