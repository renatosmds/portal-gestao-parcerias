from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
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
