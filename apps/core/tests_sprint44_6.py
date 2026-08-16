from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    FolhaPagamento,
    FolhaPonto,
    Funcionario,
)
from apps.lancamentos.models import Lancamento
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PGPRulesRHSprint446Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC RH Sprint 44.6"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RH446/26",
            termo="Termo RH 44.6",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
        )

        self.user = User.objects.create_user(
            username="rh446"
        )

        self.funcionario = Funcionario.objects.create(
            nome="Trabalhador RH 44.6",
            usuario="rh446",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Cidade ficticia",
            estado="MG",
            email="rh446@example.invalid",
            Telefone="000000000",
            salarioBase=Decimal("3000.00"),
            fgts=Decimal("240.00"),
            inss=Decimal("300.00"),
            tipo_vinculo="clt",
            data_admissao=date(2026, 1, 1),
            divisor_mensal=220,
            termo=self.termo,
            empresa=self.empresa,
            user=self.user,
            imagem="funcionarios/rh446.jpg",
        )

        self.ponto = FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(2026, 7, 1),
            horas_previstas=Decimal("176.00"),
            horas_trabalhadas=Decimal("176.00"),
            horas_extras=Decimal("0.00"),
            horas_faltas_atrasos=Decimal("0.00"),
            banco_horas=Decimal("0.00"),
            status="fechada",
        )

        self.folha = FolhaPagamento.objects.create(
            funcionario=self.funcionario,
            folha_ponto=self.ponto,
            competencia=date(2026, 7, 1),
            salario_base=Decimal("3000.00"),
            inss=Decimal("300.00"),
            status="fechada",
        )

    def criar_lancamento(
        self,
        numero="RH446-001",
        valor=None,
        data_documento=date(2026, 7, 10),
        numero_documento="FOLHA-07-2026",
    ):
        if valor is None:
            valor = self.folha.valor_liquido

        return Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento=numero,
            tipo_documento=Lancamento.TipoDocumento.FOLHA,
            numero_documento=numero_documento,
            data_documento=data_documento,
            data_pagamento=date(2026, 7, 10),
            descricao="Folha de pagamento RH 44.6",
            valor_documento=valor,
            comprovante_pagamento="pagamentos/rh446.pdf",
        )

    def vincular_documento(
        self,
        lancamento,
        descricao="folha446",
    ):
        return Documento.objects.create(
            descricao=descricao,
            arquivo=f"documentos/{descricao}.pdf",
            pertence=self.funcionario,
            empresa=self.empresa,
            termo=self.termo,
            lancamento=lancamento,
            tipo=Documento.Tipo.FOLHA,
            status=Documento.Status.CONFERIDO,
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=True,
            atesto_valido=True,
        )

    def test_lancamento_vinculado_e_compativel(self):
        lancamento = self.criar_lancamento()

        self.vincular_documento(
            lancamento
        )

        resultado = motor_regras.analisar_conciliacao_rh(
            self.folha
        )

        self.assertEqual(
            resultado.total_achados,
            0,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "conciliado_sem_inconsistencia_detectada",
        )

    def test_lancamento_nao_localizado_gera_alerta(self):
        resultado = motor_regras.analisar_conciliacao_rh(
            self.folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_LANCAMENTO_NAO_LOCALIZADO",
            codigos,
        )

    def test_valor_nao_conciliado_gera_alerta(self):
        lancamento = self.criar_lancamento(
            valor=Decimal("5000.00")
        )

        self.vincular_documento(
            lancamento
        )

        resultado = motor_regras.analisar_conciliacao_rh(
            self.folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_LANC_VALOR_NAO_CONCILIADO",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "requer_conferencia",
        )

    def test_competencia_divergente_e_critica(self):
        lancamento = self.criar_lancamento(
            data_documento=date(2026, 8, 10)
        )

        self.vincular_documento(
            lancamento
        )

        resultado = motor_regras.analisar_conciliacao_rh(
            self.folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_LANC_COMPETENCIA_DIVERGENTE",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_conciliacao_nao_altera_folha_ou_lancamento(self):
        lancamento = self.criar_lancamento(
            valor=Decimal("5000.00")
        )

        self.vincular_documento(
            lancamento
        )

        situacao_antes = lancamento.situacao
        glosa_antes = lancamento.valor_glosa
        salario_antes = self.folha.salario_base

        motor_regras.analisar_conciliacao_rh(
            self.folha
        )

        lancamento.refresh_from_db()
        self.folha.refresh_from_db()

        self.assertEqual(
            lancamento.situacao,
            situacao_antes,
        )

        self.assertEqual(
            lancamento.valor_glosa,
            glosa_antes,
        )

        self.assertEqual(
            self.folha.salario_base,
            salario_antes,
        )
