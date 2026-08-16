from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PGPRulesLancamentosSprint43Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Teste Sprint 43"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="SPRINT43/2026",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
            valorglobal=Decimal("100000.00"),
        )

    def criar_lancamento(self, numero="LANC-001"):
        return Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento=numero,
            tipo_documento=Lancamento.TipoDocumento.NFE,
            numero_documento=f"NF-{numero}",
            data_documento=date(2026, 7, 1),
            data_pagamento=date(2026, 7, 2),
            descricao="Despesa de teste",
            valor_documento=Decimal("1000.00"),
        )

    def criar_documento_regular(self, lancamento):
        return Documento.objects.create(
            descricao="Nota fiscal teste",
            arquivo="documentos/teste_sprint43.pdf",
            empresa=self.empresa,
            lancamento=lancamento,
            tipo=Documento.Tipo.NOTA_FISCAL,
            numero_documento=lancamento.numero_documento,
            data_documento=lancamento.data_documento,
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=True,
            atesto_valido=True,
        )

    def test_lancamento_sem_documento_gera_pendencia_critica(self):
        lancamento = self.criar_lancamento()

        resultado = motor_regras.analisar_lancamento(
            lancamento
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "LANC_SEM_DOCUMENTO",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_documento_irregular_propaga_achado(self):
        lancamento = self.criar_lancamento()

        Documento.objects.create(
            descricao="Nota fiscal irregular",
            arquivo="documentos/teste_irregular.pdf",
            empresa=self.empresa,
            lancamento=lancamento,
            tipo=Documento.Tipo.NOTA_FISCAL,
            numero_documento=lancamento.numero_documento,
            data_documento=lancamento.data_documento,
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=False,
            atesto_valido=True,
        )

        resultado = motor_regras.analisar_lancamento(
            lancamento
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "SEM_COMPROVANTE_PAGAMENTO",
            codigos,
        )

        self.assertTrue(
            resultado.possui_risco_glosa
        )

    def test_lancamento_regular_sem_inconsistencia(self):
        lancamento = self.criar_lancamento()

        self.criar_documento_regular(
            lancamento
        )

        resultado = motor_regras.analisar_lancamento(
            lancamento
        )

        self.assertEqual(
            resultado.total_achados,
            0,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "sem_inconsistencia_detectada",
        )

    def test_motor_nao_altera_decisao_humana(self):
        lancamento = self.criar_lancamento()

        lancamento.situacao = Lancamento.Situacao.RESSALVA
        lancamento.tipo_glosa = Lancamento.TipoGlosa.PARCIAL
        lancamento.valor_glosa = Decimal("100.00")
        lancamento.justificativa = "Decisao humana"
        lancamento.recomendacao = "Recomendacao humana"

        lancamento.save(
            update_fields=[
                "situacao",
                "tipo_glosa",
                "valor_glosa",
                "justificativa",
                "recomendacao",
            ]
        )

        Documento.objects.create(
            descricao="Documento com pendencia",
            arquivo="documentos/teste_preserva.pdf",
            empresa=self.empresa,
            lancamento=lancamento,
            tipo=Documento.Tipo.NOTA_FISCAL,
            numero_documento=lancamento.numero_documento,
            data_documento=lancamento.data_documento,
            documento_legivel=False,
            dados_compativeis=False,
            vigencia_valida=False,
            pagamento_comprovado=False,
            atesto_valido=False,
        )

        motor_regras.analisar_lancamento(
            lancamento
        )

        lancamento.refresh_from_db()

        self.assertEqual(
            lancamento.situacao,
            Lancamento.Situacao.RESSALVA,
        )

        self.assertEqual(
            lancamento.tipo_glosa,
            Lancamento.TipoGlosa.PARCIAL,
        )

        self.assertEqual(
            lancamento.valor_glosa,
            Decimal("100.00"),
        )

        self.assertEqual(
            lancamento.justificativa,
            "Decisao humana",
        )

        self.assertEqual(
            lancamento.recomendacao,
            "Recomendacao humana",
        )

