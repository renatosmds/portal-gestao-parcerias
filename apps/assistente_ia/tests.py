from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.documentos.models import Documento
from apps.empresas.models import Empresa

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
