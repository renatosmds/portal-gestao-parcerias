from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from apps.empresas.models import Empresa
from apps.prestacao.models import Prestacao
from .models import Conciliacao, Movimentacao
from .services import importar_extrato


class ConciliacaoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("admin25", "admin25@example.com", "senha123")
        self.empresa = Empresa.objects.create(nome="OSC Sprint 25")
        self.prestacao = Prestacao.objects.create(tipoTermo="TC", numtermo="025/2026", tipo="cnpj", empresa=self.empresa)
        self.conciliacao = Conciliacao.objects.create(prestacao=self.prestacao, saldo_inicial=Decimal("100.00"), saldo_final_informado=Decimal("130.00"), criado_por=self.user)

    def test_saldo_calculado(self):
        Movimentacao.objects.create(conciliacao=self.conciliacao, data="2026-07-01", descricao="Repasse", tipo="credito", valor=Decimal("50.00"))
        Movimentacao.objects.create(conciliacao=self.conciliacao, data="2026-07-02", descricao="Pagamento", tipo="debito", valor=Decimal("20.00"))
        self.assertEqual(self.conciliacao.saldo_final_calculado, Decimal("130.00"))

    def test_importacao_csv(self):
        arq = SimpleUploadedFile("extrato.csv", "data;descricao;credito;debito\n01/07/2026;Repasse;100,00;\n02/07/2026;Compra;;25,50\n".encode(), content_type="text/csv")
        imp = importar_extrato(self.conciliacao, arq, self.user)
        self.assertEqual(imp.total_importadas, 2)
        self.assertEqual(self.conciliacao.movimentacoes.count(), 2)

    def test_painel_exige_login(self):
        resposta = self.client.get(reverse("conciliacao_painel"))
        self.assertEqual(resposta.status_code, 302)

    def test_superusuario_acessa_painel(self):
        self.client.force_login(self.user)
        resposta = self.client.get(reverse("conciliacao_painel"))
        self.assertEqual(resposta.status_code, 200)

    def test_recalculo_fechada_apos_conciliacao(self):
        mov = Movimentacao.objects.create(conciliacao=self.conciliacao, data="2026-07-03", descricao="Ajuste", tipo="credito", valor=Decimal("30.00"), situacao=Movimentacao.Situacao.CONCILIADA)
        self.conciliacao.recalcular_situacao()
        self.assertEqual(self.conciliacao.situacao, Conciliacao.Situacao.FECHADA)
