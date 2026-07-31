from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.documentos.models import Documento
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
