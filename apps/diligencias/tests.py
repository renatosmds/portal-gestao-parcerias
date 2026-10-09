from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

class DiligenciasRoutesTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("teste_s19", "teste@example.com", "senha-forte")
        self.client.force_login(self.user)

    def test_listagem_renderiza_conteudo(self):
        response = self.client.get(reverse("list_diligencias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Central de Diligências")
        self.assertContains(response, "Nova diligência")

    def test_cadastro_abre(self):
        response = self.client.get(reverse("create_diligencia"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nova diligência")


class DiligenciasPermissaoModuloTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="usuario_sem_diligencias",
            password="teste12345",
        )

    def test_usuario_sem_permissao_nao_acessa_lista_por_url(self):
        self.client.force_login(
            self.usuario
        )

        response = self.client.get(
            reverse("list_diligencias")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_usuario_com_permissao_acessa_modulo(self):
        permissao = Permission.objects.get(
            content_type__app_label="diligencias",
            codename="view_diligencia",
        )

        self.usuario.user_permissions.add(
            permissao
        )

        self.client.force_login(
            self.usuario
        )

        response = self.client.get(
            reverse("list_diligencias")
        )

        self.assertEqual(
            response.status_code,
            200,
        )


class DiligenciasEscopoMultiempresaTests(TestCase):

    def setUp(self):
        from apps.diligencias.models import Diligencia
        from apps.empresas.models import Empresa
        from apps.funcionarios.models import Funcionario

        User = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="OSC A Diligencias",
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC B Diligencias",
        )

        self.usuario_a = User.objects.create_user(
            username="staff_diligencias_a",
            password="teste12345",
            is_staff=True,
        )

        self.usuario_b = User.objects.create_user(
            username="staff_diligencias_b",
            password="teste12345",
            is_staff=True,
        )

        self.staff_sem_empresa = User.objects.create_user(
            username="staff_diligencias_sem_empresa",
            password="teste12345",
            is_staff=True,
        )

        self.superusuario = User.objects.create_superuser(
            username="admin_diligencias_global",
            email="admin-diligencias@example.test",
            password="teste12345",
        )

        Funcionario.objects.create(
            cpf="52998224725",
            nome="Staff Diligencias A",
            usuario="staff_diligencias_a",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="staff_diligencias_a@example.test",
            Telefone="000000000",
            user=self.usuario_a,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
        )

        Funcionario.objects.create(
            cpf="16899535009",
            nome="Staff Diligencias B",
            usuario="staff_diligencias_b",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="staff_diligencias_b@example.test",
            Telefone="000000000",
            user=self.usuario_b,
            empresa=self.empresa_b,
            imagem="funcionarios/teste.jpg",
        )

        permissao = Permission.objects.get(
            content_type__app_label="diligencias",
            codename="view_diligencia",
        )

        self.usuario_a.user_permissions.add(
            permissao
        )

        self.usuario_b.user_permissions.add(
            permissao
        )

        self.staff_sem_empresa.user_permissions.add(
            permissao
        )

        self.diligencia_a = Diligencia.objects.create(
            assunto="Diligencia Empresa A",
            descricao="Teste de isolamento da empresa A",
            empresa=self.empresa_a,
            criada_por=self.superusuario,
        )

        self.diligencia_b = Diligencia.objects.create(
            assunto="Diligencia Empresa B",
            descricao="Teste de isolamento da empresa B",
            empresa=self.empresa_b,
            criada_por=self.superusuario,
        )

    def test_staff_empresa_a_ve_apenas_diligencia_da_empresa_a(self):
        self.client.force_login(
            self.usuario_a
        )

        response = self.client.get(
            reverse("list_diligencias")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        diligencias = list(
            response.context["diligencias"]
        )

        self.assertEqual(
            diligencias,
            [self.diligencia_a],
        )

    def test_staff_empresa_b_nao_acessa_diligencia_da_empresa_a(self):
        self.client.force_login(
            self.usuario_b
        )

        response = self.client.get(
            reverse(
                "detail_diligencia",
                args=[self.diligencia_a.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_staff_sem_empresa_nao_recebe_diligencias(self):
        self.client.force_login(
            self.staff_sem_empresa
        )

        response = self.client.get(
            reverse("list_diligencias")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            list(response.context["diligencias"]),
            [],
        )

    def test_superusuario_recebe_visao_global(self):
        self.client.force_login(
            self.superusuario
        )

        response = self.client.get(
            reverse("list_diligencias")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        ids = {
            item.pk
            for item in response.context["diligencias"]
        }

        self.assertEqual(
            ids,
            {
                self.diligencia_a.pk,
                self.diligencia_b.pk,
            },
        )


class DiligenciasGestorMunicipalTests(TestCase):

    def setUp(self):
        from django.contrib.auth.models import Group
        from apps.diligencias.models import Diligencia
        from apps.empresas.models import Empresa

        User = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="OSC A Diligencia Gestor",
        )
        self.empresa_b = Empresa.objects.create(
            nome="OSC B Diligencia Gestor",
        )

        self.criador = User.objects.create_superuser(
            username="admin_dilig_gestor_fixture",
            email="admin-dilig-gestor@example.test",
            password="teste12345",
        )

        self.diligencia_a = Diligencia.objects.create(
            assunto="Diligencia Gestor A",
            descricao="Teste global A",
            empresa=self.empresa_a,
            criada_por=self.criador,
        )

        self.diligencia_b = Diligencia.objects.create(
            assunto="Diligencia Gestor B",
            descricao="Teste global B",
            empresa=self.empresa_b,
            criada_por=self.criador,
        )

        self.gestor = User.objects.create_user(
            username="gestor_diligencias_global",
            password="teste12345",
        )

        permissoes = Permission.objects.filter(
            content_type__app_label="diligencias",
        )
        self.gestor.user_permissions.add(*permissoes)

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal",
        )
        self.gestor.groups.add(grupo)

    def test_gestor_municipal_recebe_visao_global(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("list_diligencias")
        )

        self.assertEqual(response.status_code, 200)

        ids = {
            item.pk
            for item in response.context["diligencias"]
        }

        self.assertEqual(
            ids,
            {
                self.diligencia_a.pk,
                self.diligencia_b.pk,
            },
        )
