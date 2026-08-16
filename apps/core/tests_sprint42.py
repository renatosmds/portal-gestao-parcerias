from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.regras.engine import motor_regras


class PGPRulesSprint42Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Teste Rules"
        )

        self.lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            numero_lancamento="RULE-001",
            tipo_documento=Lancamento.TipoDocumento.NFE,
            numero_documento="NF-001",
            data_documento=date(2026, 7, 1),
            data_pagamento=None,
            descricao="Despesa teste",
            valor_documento=Decimal("1000.00"),
        )

        self.documento = Documento.objects.create(
            descricao="Nota fiscal teste",
            arquivo="documentos/teste_rules.pdf",
            empresa=self.empresa,
            lancamento=self.lancamento,
            tipo=Documento.Tipo.NOTA_FISCAL,
            numero_documento="NF-001",
            data_documento=date(2026, 7, 1),
            documento_legivel=True,
            dados_compativeis=True,
            pagamento_comprovado=False,
            atesto_valido=True,
        )

    def test_motor_identifica_pagamento_nao_comprovado(self):
        resultados = motor_regras.analisar_documento(
            self.documento
        )

        codigos = {
            resultado.codigo
            for resultado in resultados
        }

        self.assertIn(
            "SEM_COMPROVANTE_PAGAMENTO",
            codigos,
        )

    def test_resultado_possui_campos_auditaveis(self):
        resultados = motor_regras.analisar_documento(
            self.documento
        )

        resultado = next(
            item
            for item in resultados
            if item.codigo == "SEM_COMPROVANTE_PAGAMENTO"
        )

        self.assertEqual(
            resultado.categoria,
            "documental",
        )

        self.assertTrue(
            resultado.fato_verificado
        )

        self.assertTrue(
            resultado.risco_glosa
        )

        self.assertTrue(
            resultado.recomendacao
        )

    def test_motor_nao_aplica_glosa_automaticamente(self):
        situacao_antes = self.lancamento.situacao
        tipo_glosa_antes = self.lancamento.tipo_glosa
        valor_glosa_antes = self.lancamento.valor_glosa

        motor_regras.analisar_documento(
            self.documento
        )

        self.lancamento.refresh_from_db()

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

    def test_motor_nao_altera_justificativa_ou_recomendacao(self):
        self.lancamento.justificativa = "Texto humano original"
        self.lancamento.recomendacao = "Recomendacao humana original"
        self.lancamento.save(
            update_fields=[
                "justificativa",
                "recomendacao",
            ]
        )

        motor_regras.analisar_documento(
            self.documento
        )

        self.lancamento.refresh_from_db()

        self.assertEqual(
            self.lancamento.justificativa,
            "Texto humano original",
        )

        self.assertEqual(
            self.lancamento.recomendacao,
            "Recomendacao humana original",
        )
