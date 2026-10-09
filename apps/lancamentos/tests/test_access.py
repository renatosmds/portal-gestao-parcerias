from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from apps.core.testes_documentos import cpf_teste
from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.lancamentos.models import Lancamento


class LancamentoAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.empresa = Empresa.objects.create(nome="Empresa Lançamentos")
        cls.lancamento = Lancamento.objects.create(
            empresa=cls.empresa,
            numero_lancamento="164578",
            data_documento=date(2026, 5, 22),
            descricao="Despesa de teste",
            valor_documento=Decimal("230.29"),
        )
        cls.user = User.objects.create_user(
            username="lancamento_teste",
            password="senha-teste-123",
        )

    def test_lista_exige_login(self):
        self.assertEqual(
            self.client.get(reverse("list_lancamentos")).status_code,
            302,
        )

    def test_usuario_sem_permissao_recebe_403(self):
        self.client.force_login(self.user)
        self.assertEqual(
            self.client.get(reverse("list_lancamentos")).status_code,
            403,
        )

    def test_superuser_visualiza_lista(self):
        admin = User.objects.create_superuser(
            username="admin_lancamento",
            email="admin@example.com",
            password="senha-teste-123",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("list_lancamentos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "164578")

    def test_calculo_valor_aprovado(self):
        self.lancamento.valor_glosa = Decimal("30.29")
        self.assertEqual(
            self.lancamento.valor_aprovado,
            Decimal("200.00"),
        )

class LancamentoEscopoMultiempresaTests(TestCase):

    def setUp(self):
        UserModel = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="Empresa Lancamento A",
        )
        self.empresa_b = Empresa.objects.create(
            nome="Empresa Lancamento B",
        )

        self.lancamento_a = Lancamento.objects.create(
            empresa=self.empresa_a,
            numero_lancamento="ESC-A-001",
            data_documento=date(2026, 8, 1),
            descricao="Lancamento empresa A",
            valor_documento=Decimal("100.00"),
        )

        self.lancamento_b = Lancamento.objects.create(
            empresa=self.empresa_b,
            numero_lancamento="ESC-B-001",
            data_documento=date(2026, 8, 2),
            descricao="Lancamento empresa B",
            valor_documento=Decimal("200.00"),
        )

        self.permissao = Permission.objects.get(
            content_type__app_label="lancamentos",
            codename="view_lancamento",
        )

        self.usuario_a = UserModel.objects.create_user(
            username="lanc_escopo_a",
            password="teste12345",
        )
        self.usuario_a.user_permissions.add(self.permissao)

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Usuario Lancamento A",
            usuario="lanc_escopo_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="lanc-a@example.test",
            Telefone="-",
            user=self.usuario_a,
            empresa=self.empresa_a,
            imagem="funcionarios_photos/teste.jpg",
        )

        self.staff_a = UserModel.objects.create_user(
            username="lanc_staff_a",
            password="teste12345",
            is_staff=True,
        )
        self.staff_a.user_permissions.add(self.permissao)

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Staff Lancamento A",
            usuario="lanc_staff_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="lanc-staff-a@example.test",
            Telefone="-",
            user=self.staff_a,
            empresa=self.empresa_a,
            imagem="funcionarios_photos/teste.jpg",
        )

        self.usuario_b = UserModel.objects.create_user(
            username="lanc_escopo_b",
            password="teste12345",
        )
        self.usuario_b.user_permissions.add(self.permissao)

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Usuario Lancamento B",
            usuario="lanc_escopo_b",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="lanc-b@example.test",
            Telefone="-",
            user=self.usuario_b,
            empresa=self.empresa_b,
            imagem="funcionarios_photos/teste.jpg",
        )

        self.usuario_sem_empresa = UserModel.objects.create_user(
            username="lanc_sem_empresa",
            password="teste12345",
        )
        self.usuario_sem_empresa.user_permissions.add(
            self.permissao
        )

        self.gestor = UserModel.objects.create_user(
            username="lanc_gestor",
            password="teste12345",
        )
        self.gestor.user_permissions.add(self.permissao)

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal"
        )
        self.gestor.groups.add(grupo)

    def test_usuario_empresa_a_ve_apenas_lancamentos_da_empresa_a(self):
        self.client.force_login(self.usuario_a)

        response = self.client.get(
            reverse("list_lancamentos")
        )

        self.assertEqual(response.status_code, 200)

        ids = {
            obj.pk
            for obj in response.context["lancamentos"]
        }

        self.assertEqual(
            ids,
            {self.lancamento_a.pk},
        )

    def test_staff_comum_nao_ganha_visao_global(self):
        self.client.force_login(self.staff_a)

        response = self.client.get(
            reverse("list_lancamentos")
        )

        self.assertEqual(response.status_code, 200)

        ids = {
            obj.pk
            for obj in response.context["lancamentos"]
        }

        self.assertEqual(
            ids,
            {self.lancamento_a.pk},
        )

    def test_empresa_b_nao_acessa_detalhe_da_empresa_a(self):
        self.client.force_login(self.usuario_b)

        response = self.client.get(
            reverse(
                "detail_lancamento",
                kwargs={"pk": self.lancamento_a.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_usuario_sem_empresa_nao_recebe_lancamentos(self):
        self.client.force_login(
            self.usuario_sem_empresa
        )

        response = self.client.get(
            reverse("list_lancamentos")
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            list(response.context["lancamentos"]),
            [],
        )

    def test_gestor_municipal_recebe_visao_global(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("list_lancamentos")
        )

        self.assertEqual(response.status_code, 200)

        ids = {
            obj.pk
            for obj in response.context["lancamentos"]
        }

        self.assertEqual(
            ids,
            {
                self.lancamento_a.pk,
                self.lancamento_b.pk,
            },
        )
