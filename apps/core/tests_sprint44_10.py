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


class PGPRulesRHSprint4410Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC RH Sprint 44.10"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RH4410/26",
            termo="Termo RH 44.10",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
        )

        self.user = User.objects.create_user(
            username="rh4410"
        )

        self.funcionario = Funcionario.objects.create(
            nome="Trabalhador RH 44.10",
            usuario="rh4410",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Cidade ficticia",
            estado="MG",
            email="rh4410@example.invalid",
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
            imagem="funcionarios/rh4410.jpg",
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

        self.lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento="RH4410-001",
            tipo_documento=Lancamento.TipoDocumento.FOLHA,
            numero_documento="FOLHA-RH4410",
            data_documento=date(2026, 7, 10),
            data_pagamento=date(2026, 7, 10),
            descricao="Folha de pagamento RH 44.10",
            valor_documento=self.folha.valor_liquido,
            comprovante_pagamento="pagamentos/rh4410.pdf",
        )

        Documento.objects.create(
            descricao="Folha RH 44.10",
            arquivo="documentos/folha4410.pdf",
            pertence=self.funcionario,
            empresa=self.empresa,
            termo=self.termo,
            lancamento=self.lancamento,
            tipo=Documento.Tipo.FOLHA,
            status=Documento.Status.CONFERIDO,
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=True,
            atesto_valido=True,
        )

        Documento.objects.create(
            descricao="Comprovante RH 44.10",
            arquivo="documentos/pagamento4410.pdf",
            pertence=self.funcionario,
            empresa=self.empresa,
            termo=self.termo,
            lancamento=self.lancamento,
            tipo=Documento.Tipo.COMPROVANTE,
            status=Documento.Status.CONFERIDO,
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=True,
            atesto_valido=True,
        )

        Documento.objects.create(
            descricao="Guia RH 44.10",
            arquivo="documentos/guia4410.pdf",
            pertence=self.funcionario,
            empresa=self.empresa,
            termo=self.termo,
            tipo=Documento.Tipo.GUIA,
            status=Documento.Status.CONFERIDO,
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=True,
            atesto_valido=True,
        )

    def test_consolida_todas_as_camadas(self):
        resultado = motor_regras.analisar_rh_completo(
            self.folha
        )

        self.assertIsNotNone(
            resultado.analise_folha
        )

        self.assertIsNotNone(
            resultado.analise_documental
        )

        self.assertIsNotNone(
            resultado.analise_conciliacao
        )

        self.assertIsNotNone(
            resultado.analise_composicao
        )

        self.assertIsNotNone(
            resultado.analise_verbas
        )

        self.assertIsNotNone(
            resultado.analise_lgpd
        )

    def test_achados_sao_ordenados_por_gravidade(self):
        self.ponto.competencia = date(2026, 6, 1)
        self.ponto.save(
            update_fields=["competencia"]
        )

        resultado = motor_regras.analisar_rh_completo(
            self.folha
        )

        severidades = [
            item.severidade
            for item in resultado.achados
        ]

        if "critico" in severidades and "alerta" in severidades:
            self.assertLess(
                severidades.index("critico"),
                severidades.index("alerta"),
            )

    def test_conclusao_executiva_critica(self):
        self.funcionario.data_admissao = date(2026, 8, 1)

        self.funcionario.save(
            update_fields=[
                "data_admissao",
            ]
        )

        resultado = motor_regras.analisar_rh_completo(
            self.folha
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

        self.assertGreater(
            resultado.total_criticos,
            0,
        )

        self.assertIn(
            "pendências críticas",
            resultado.conclusao_executiva,
        )

    def test_resumo_executivo_nao_expoe_dados_pessoais(self):
        self.funcionario.cpf = "000.000.000-00"
        self.funcionario.conta_bancaria = "12345-6"

        self.funcionario.save(
            update_fields=[
                "cpf",
                "conta_bancaria",
            ]
        )

        resultado = motor_regras.analisar_rh_completo(
            self.folha,
            uso_ia=True,
            dados_minimizados=True,
        )

        resumo = str(
            resultado.resumo_executivo()
        )

        self.assertNotIn(
            "000.000.000-00",
            resumo,
        )

        self.assertNotIn(
            "12345-6",
            resumo,
        )

    def test_motor_consolidado_nao_aplica_glosa(self):
        situacao_antes = self.lancamento.situacao
        tipo_glosa_antes = self.lancamento.tipo_glosa
        valor_glosa_antes = self.lancamento.valor_glosa
        salario_antes = self.folha.salario_base

        motor_regras.analisar_rh_completo(
            self.folha
        )

        self.lancamento.refresh_from_db()
        self.folha.refresh_from_db()

        self.assertEqual(
            self.lancamento.situacao,
            situacao_antes,
        )

        self.assertEqual(
            self.lancamento.tipo_glosa,
            tipo_glosa_antes,
        )

        self.assertEqual(
            self.lancamento.valor_glosa,
            valor_glosa_antes,
        )

        self.assertEqual(
            self.folha.salario_base,
            salario_antes,
        )
