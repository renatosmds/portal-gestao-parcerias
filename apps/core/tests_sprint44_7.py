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
from apps.regras.rules.rh_composicao import (
    calcular_composicao_despesa_rh,
)
from apps.termos.models import Termos


class PGPRulesRHSprint447Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC RH Sprint 44.7"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RH447/26",
            termo="Termo RH 44.7",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
        )

        self.user = User.objects.create_user(
            username="rh447"
        )

        self.funcionario = Funcionario.objects.create(
            nome="Trabalhador RH 44.7",
            usuario="rh447",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Cidade ficticia",
            estado="MG",
            email="rh447@example.invalid",
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
            imagem="funcionarios/rh447.jpg",
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
            irrf=Decimal("100.00"),
            vale_transporte=Decimal("100.00"),
            pensao=Decimal("0.00"),
            outros_descontos=Decimal("0.00"),
            outras_verbas=Decimal("0.00"),
            status="fechada",
        )

    def criar_lancamento(
        self,
        valor,
        numero="RH447-001",
    ):
        lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento=numero,
            tipo_documento=Lancamento.TipoDocumento.FOLHA,
            numero_documento=f"FOLHA-{numero}",
            data_documento=date(2026, 7, 10),
            data_pagamento=date(2026, 7, 10),
            descricao="Despesa RH 44.7",
            valor_documento=valor,
        )

        Documento.objects.create(
            descricao=f"doc-{numero}",
            arquivo=f"documentos/{numero}.pdf",
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

        return lancamento

    def test_calcula_composicao_basica(self):
        composicao = calcular_composicao_despesa_rh(
            self.folha
        )

        self.assertEqual(
            composicao.salario_base,
            Decimal("3000.00"),
        )

        self.assertEqual(
            composicao.fgts,
            Decimal("240.00"),
        )

        self.assertEqual(
            composicao.total_proventos,
            Decimal("3000.00"),
        )

        self.assertEqual(
            composicao.valor_liquido,
            Decimal("2500.00"),
        )

        self.assertEqual(
            composicao.valor_potencialmente_elegivel,
            Decimal("3240.00"),
        )

    def test_valor_lancado_superior_gera_critico(self):
        self.criar_lancamento(
            Decimal("3500.00")
        )

        resultado = motor_regras.analisar_composicao_rh(
            self.folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_VALOR_LANCADO_SUPERIOR_POTENCIAL",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_valor_lancado_inferior_e_informativo(self):
        self.criar_lancamento(
            Decimal("3000.00")
        )

        resultado = motor_regras.analisar_composicao_rh(
            self.folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_VALOR_LANCADO_INFERIOR_POTENCIAL",
            codigos,
        )

    def test_faltas_reduzem_valor_potencial(self):
        self.ponto.horas_trabalhadas = Decimal("168.00")
        self.ponto.horas_faltas_atrasos = Decimal("8.00")

        self.ponto.save(
            update_fields=[
                "horas_trabalhadas",
                "horas_faltas_atrasos",
            ]
        )

        composicao = calcular_composicao_despesa_rh(
            self.folha
        )

        self.assertGreater(
            composicao.faltas_atrasos,
            Decimal("0.00"),
        )

        self.assertLess(
            composicao.valor_potencialmente_elegivel,
            Decimal("3240.00"),
        )

    def test_motor_nao_aplica_glosa(self):
        lancamento = self.criar_lancamento(
            Decimal("3500.00")
        )

        situacao_antes = lancamento.situacao
        tipo_glosa_antes = lancamento.tipo_glosa
        valor_glosa_antes = lancamento.valor_glosa

        motor_regras.analisar_composicao_rh(
            self.folha
        )

        lancamento.refresh_from_db()

        self.assertEqual(
            lancamento.situacao,
            situacao_antes,
        )

        self.assertEqual(
            lancamento.tipo_glosa,
            tipo_glosa_antes,
        )

        self.assertEqual(
            lancamento.valor_glosa,
            valor_glosa_antes,
        )
