from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.termos.models import Termos


class TermosAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Termo")
        cls.termo = Termos.objects.create(
            termo="TC 001/2026",
            nomeosc="OSC Teste",
            empresa=cls.empresa,
        )
        cls.user = User.objects.create_user(
            username="termo_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        self.assertEqual(self.client.get(reverse("list_termos")).status_code, 302)

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("list_termos")).status_code, 403)

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_termo",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("list_termos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TC 001/2026")

    def test_str_nunca_retorna_none(self):
        vazio = Termos.objects.create(empresa=self.empresa)
        self.assertEqual(str(vazio), f"Termo #{vazio.pk}")

class TermosIsolamentoEmpresaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa_a = Empresa.objects.create(
            nome="Empresa A Termos"
        )
        cls.empresa_b = Empresa.objects.create(
            nome="Empresa B Termos"
        )

        cls.termo_a = Termos.objects.create(
            termo="TC A",
            numtermo="TA-001/2026",
            nomeosc="OSC A",
            empresa=cls.empresa_a,
        )
        cls.termo_b = Termos.objects.create(
            termo="TC B",
            numtermo="TB-001/2026",
            nomeosc="OSC B",
            empresa=cls.empresa_b,
        )

        cls.user = User.objects.create_user(
            username="termo_empresa_a",
            password="teste123",
        )

        permissoes = Permission.objects.filter(
            codename__in=[
                "view_termos",
                "change_termos",
                "delete_termos",
            ]
        )
        cls.user.user_permissions.add(*permissoes)

        Funcionario.objects.create(
            nome="Usuario Termos Empresa A",
            usuario="termo_empresa_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="-",
            estado="MG",
            email="termos-a@example.com",
            Telefone="-",
            user=cls.user,
            empresa=cls.empresa_a,
            imagem="funcionarios_photos/teste.jpg",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_lista_nao_exibe_termo_de_outra_empresa(self):
        response = self.client.get(
            reverse("list_termos")
        )

        self.assertEqual(response.status_code, 200)

        termos = list(response.context["termos"])

        self.assertIn(self.termo_a, termos)
        self.assertNotIn(self.termo_b, termos)
        self.assertEqual(len(termos), 1)

    def test_detalhe_de_outra_empresa_retorna_404(self):
        response = self.client.get(
            reverse(
                "detail_termo",
                kwargs={"pk": self.termo_b.pk},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_edicao_de_outra_empresa_retorna_404(self):
        response = self.client.get(
            reverse(
                "update_termos",
                kwargs={"pk": self.termo_b.pk},
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_exclusao_de_outra_empresa_retorna_404(self):
        response = self.client.get(
            reverse(
                "delete_termos",
                kwargs={"pk": self.termo_b.pk},
            )
        )
        self.assertEqual(response.status_code, 404)
