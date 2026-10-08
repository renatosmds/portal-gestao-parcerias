from datetime import date

from django.contrib.auth import get_user_model
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
