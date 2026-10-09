from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario

from .models import ProcessamentoAssistido
from .services import validar_documento


class AssistenteIALocalTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin_ia", email="admin@example.com", password="teste12345"
        )
        self.empresa = Empresa.objects.create(nome="OSC Teste")
        self.documento = Documento.objects.create(
            descricao="Nota fiscal teste",
            arquivo="documentos/teste.pdf",
            empresa=self.empresa,
            tipo=Documento.Tipo.NOTA_FISCAL,
            numero_documento="NF-001",
            data_documento=date(2026, 7, 1),
        )

    def test_validacao_identifica_ausencia_de_lancamento(self):
        codigos = {item["codigo"] for item in validar_documento(self.documento)}
        self.assertIn("SEM_LANCAMENTO", codigos)

    def test_superusuario_acessa_central(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("assistente_ia_central"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Central de Análise Assistida")

    def test_execucao_cria_processamento(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("assistente_ia_executar", kwargs={"pk": self.documento.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProcessamentoAssistido.objects.count(), 1)
        self.assertGreater(ProcessamentoAssistido.objects.first().achados.count(), 0)


class AssistenteIAMultiempresaTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="OSC Empresa A"
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC Empresa B"
        )

        self.usuario_a = User.objects.create_user(
            username="usuario_empresa_a",
            password="teste12345",
            is_staff=True,
        )

        self.funcionario_a = Funcionario.objects.create(
            user=self.usuario_a,
            nome="Usuario Empresa A",
            cpf="52998224725",
            empresa=self.empresa_a,
        )

        self.documento_a = Documento.objects.create(
            descricao="Documento A",
            arquivo="documentos/a.pdf",
            empresa=self.empresa_a,
            tipo=Documento.Tipo.NOTA_FISCAL,
        )

        permissoes_ia = Permission.objects.filter(
            content_type__app_label="assistente_ia",
        )
        self.usuario_a.user_permissions.add(
            *permissoes_ia
        )

        self.documento_b = Documento.objects.create(
            descricao="Documento B",
            arquivo="documentos/b.pdf",
            empresa=self.empresa_b,
            tipo=Documento.Tipo.NOTA_FISCAL,
        )

    def test_staff_ve_apenas_documentos_da_propria_empresa(self):
        self.client.force_login(
            self.usuario_a
        )

        response = self.client.get(
            reverse("assistente_ia_central")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Documento A",
        )

        self.assertNotContains(
            response,
            "Documento B",
        )

    def test_staff_nao_processa_documento_de_outra_empresa(self):
        self.client.force_login(
            self.usuario_a
        )

        response = self.client.post(
            reverse(
                "assistente_ia_executar",
                kwargs={
                    "pk": self.documento_b.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )



class AssistenteIAGestorMunicipalTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="OSC IA Global A",
        )
        self.empresa_b = Empresa.objects.create(
            nome="OSC IA Global B",
        )

        self.doc_a = Documento.objects.create(
            descricao="Documento IA Global A",
            arquivo="documentos/ia-global-a.pdf",
            empresa=self.empresa_a,
        )
        self.doc_b = Documento.objects.create(
            descricao="Documento IA Global B",
            arquivo="documentos/ia-global-b.pdf",
            empresa=self.empresa_b,
        )

        self.gestor = User.objects.create_user(
            username="gestor_ia_global",
            password="teste12345",
        )

        permissoes = Permission.objects.filter(
            content_type__app_label="assistente_ia",
        )
        self.gestor.user_permissions.add(*permissoes)

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal",
        )
        self.gestor.groups.add(grupo)

    def test_gestor_municipal_visualiza_documentos_globais(self):
        self.client.force_login(self.gestor)

        response = self.client.get(
            reverse("assistente_ia_central")
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            "Documento IA Global A",
        )
        self.assertContains(
            response,
            "Documento IA Global B",
        )


class AssistenteIAPermissaoModuloTests(TestCase):

    def test_usuario_sem_permissao_recebe_403(self):
        User = get_user_model()

        usuario = User.objects.create_user(
            username="ia_sem_permissao",
            password="teste12345",
        )

        self.client.force_login(usuario)

        response = self.client.get(
            reverse("assistente_ia_central")
        )

        self.assertEqual(
            response.status_code,
            403,
        )
