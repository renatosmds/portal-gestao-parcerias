from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.analise.models import Analise
from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos

from .dashboard import usuario_eh_osc


class DashboardSprint15Tests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="admin_dashboard",
            email="admin@example.com",
            password="senha-forte-123",
        )
        self.empresa = Empresa.objects.create(nome="OSC Teste")
        self.termo = Termos.objects.create(
            empresa=self.empresa,
            termo="TC 001/2026",
            numtermo="001/2026",
            assinatura=date(2026, 1, 10),
            status="Vigente",
            valorglobal=Decimal("100000.00"),
            valorrepasse=Decimal("80000.00"),
            valorsaldo=Decimal("20000.00"),
        )
        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            numtermo="001/2026",
            tipo="cnpj",
            concluida=False,
        )
        self.lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            numero_lancamento="L-001",
            data_documento=date(2026, 2, 1),
            descricao="Material de consumo",
            valor_documento=Decimal("1000.00"),
            valor_glosa=Decimal("100.00"),
            situacao=Lancamento.Situacao.GLOSADO,
        )
        Documento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            lancamento=self.lancamento,
            descricao="Nota fiscal",
            arquivo=SimpleUploadedFile("nota.pdf", b"arquivo de teste"),
            status=Documento.Status.PENDENTE,
        )
        Analise.objects.create(
            empresa=self.empresa,
            numtermo=self.termo,
            prestacao=self.prestacao,
            numRA="RA-001",
            concluida=False,
        )

    def test_superusuario_acessa_dashboard_sem_funcionario_vinculado(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("home"),
            {"empresa": self.empresa.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["termos_total"], 1)
        self.assertEqual(response.context["prestacoes_abertas"], 1)
        self.assertEqual(response.context["lancamentos_total"], 1)
        self.assertEqual(response.context["documentos_pendentes"], 1)
        self.assertEqual(response.context["analises_abertas"], 1)
        self.assertEqual(response.context["valor_glosado"], Decimal("100.00"))

    def test_usuario_sem_staff_e_identificado_como_area_osc(self):
        usuario = get_user_model().objects.create_user(
            username="usuario_osc",
            password="senha-forte-123",
            is_staff=False,
        )
        self.assertTrue(usuario_eh_osc(usuario))

    def test_usuario_sem_empresa_recebe_dashboard_vazio_em_vez_de_erro_403(self):
        usuario = get_user_model().objects.create_user(
            username="usuario_sem_empresa",
            password="senha-forte-123",
        )
        self.client.force_login(usuario)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["sem_empresa_vinculada"])
        self.assertEqual(response.context["termos_total"], 0)
