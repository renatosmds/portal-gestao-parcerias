from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.regras.engine import motor_regras


class PGPRulesFinanceiroSprint43Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Financeiro Sprint 43"
        )

    def criar_lancamento(
        self,
        numero,
        numero_documento,
        valor=Decimal("1000.00"),
    ):
        return Lancamento.objects.create(
            empresa=self.empresa,
            numero_lancamento=numero,
            tipo_documento=Lancamento.TipoDocumento.NFE,
            numero_documento=numero_documento,
            data_documento=date(2026, 7, 1),
            data_pagamento=date(2026, 7, 2),
            descricao="Despesa financeira de teste",
            valor_documento=valor,
        )

    def test_sem_comprovante_pagamento_gera_achado(self):
        lancamento = self.criar_lancamento(
            "FIN-001",
            "NF-FIN-001",
        )

        Documento.objects.create(
            descricao="Nota fiscal",
            arquivo="documentos/fin001.pdf",
            empresa=self.empresa,
            lancamento=lancamento,
            tipo=Documento.Tipo.NOTA_FISCAL,
            numero_documento="NF-FIN-001",
            data_documento=date(2026, 7, 1),
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
            "FIN_SEM_COMPROVANTE_PAGAMENTO",
            codigos,
        )

    def test_comprovante_documental_evitar_alerta_financeiro(self):
        lancamento = self.criar_lancamento(
            "FIN-002",
            "NF-FIN-002",
        )

        Documento.objects.create(
            descricao="Nota fiscal",
            arquivo="documentos/fin002_nf.pdf",
            empresa=self.empresa,
            lancamento=lancamento,
            tipo=Documento.Tipo.NOTA_FISCAL,
            numero_documento="NF-FIN-002",
            data_documento=date(2026, 7, 1),
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=True,
            atesto_valido=True,
        )

        Documento.objects.create(
            descricao="Comprovante de pagamento",
            arquivo="documentos/fin002_pag.pdf",
            empresa=self.empresa,
            lancamento=lancamento,
            tipo=Documento.Tipo.COMPROVANTE,
            data_documento=date(2026, 7, 2),
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=True,
            atesto_valido=True,
        )

        resultado = motor_regras.analisar_lancamento(
            lancamento
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertNotIn(
            "FIN_SEM_COMPROVANTE_PAGAMENTO",
            codigos,
        )

    def test_possivel_duplicidade_financeira(self):
        self.criar_lancamento(
            "FIN-003-A",
            "NF-DUP-001",
        )

        lancamento = self.criar_lancamento(
            "FIN-003-B",
            "NF-DUP-001",
        )

        Documento.objects.create(
            descricao="Nota fiscal",
            arquivo="documentos/dup.pdf",
            empresa=self.empresa,
            lancamento=lancamento,
            tipo=Documento.Tipo.NOTA_FISCAL,
            numero_documento="NF-DUP-001",
            data_documento=date(2026, 7, 1),
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=True,
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
            "FIN_POSSIVEL_DUPLICIDADE",
            codigos,
        )

    def test_regra_financeira_nao_aplica_glosa(self):
        lancamento = self.criar_lancamento(
            "FIN-004",
            "NF-FIN-004",
        )

        motor_regras.analisar_lancamento(
            lancamento
        )

        lancamento.refresh_from_db()

        self.assertEqual(
            lancamento.tipo_glosa,
            Lancamento.TipoGlosa.NENHUMA,
        )

        self.assertEqual(
            lancamento.valor_glosa,
            Decimal("0.00"),
        )

        self.assertEqual(
            lancamento.situacao,
            Lancamento.Situacao.NAO_ANALISADO,
        )

