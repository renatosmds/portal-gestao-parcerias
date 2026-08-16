from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PGPRulesVigenciaSprint43Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Vigencia Sprint 43"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="VIG-001/2026",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
            valorglobal=Decimal("100000.00"),
        )

    def criar_lancamento(
        self,
        numero,
        data_documento,
        data_pagamento,
        termo=True,
    ):
        return Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo if termo else None,
            numero_lancamento=numero,
            tipo_documento=Lancamento.TipoDocumento.NFE,
            numero_documento=f"NF-{numero}",
            data_documento=data_documento,
            data_pagamento=data_pagamento,
            descricao="Despesa teste de vigencia",
            valor_documento=Decimal("1000.00"),
        )

    def test_documento_antes_da_vigencia_gera_achado(self):
        lancamento = self.criar_lancamento(
            "VIG-001",
            date(2025, 12, 20),
            date(2026, 1, 5),
        )

        resultado = motor_regras.analisar_lancamento(
            lancamento
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "VIG_DOCUMENTO_ANTES_INICIO",
            codigos,
        )

    def test_pagamento_apos_vigencia_gera_achado(self):
        lancamento = self.criar_lancamento(
            "VIG-002",
            date(2026, 12, 20),
            date(2027, 1, 10),
        )

        resultado = motor_regras.analisar_lancamento(
            lancamento
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "VIG_PAGAMENTO_APOS_FIM",
            codigos,
        )

    def test_datas_dentro_da_vigencia_nao_geram_achado_temporal(self):
        lancamento = self.criar_lancamento(
            "VIG-003",
            date(2026, 6, 10),
            date(2026, 6, 15),
        )

        resultado = motor_regras.analisar_lancamento(
            lancamento
        )

        codigos_vigencia = {
            item.codigo
            for item in resultado.achados
            if item.categoria == "vigencia"
        }

        self.assertEqual(
            codigos_vigencia,
            set(),
        )

    def test_sem_termo_retorna_nao_verificado(self):
        lancamento = self.criar_lancamento(
            "VIG-004",
            date(2026, 6, 10),
            date(2026, 6, 15),
            termo=False,
        )

        resultado = motor_regras.analisar_lancamento(
            lancamento
        )

        achado = next(
            item
            for item in resultado.achados
            if item.codigo == "VIG_TERMO_NAO_VINCULADO"
        )

        self.assertEqual(
            achado.resultado,
            "nao_verificado",
        )

        self.assertEqual(
            achado.categoria,
            "vigencia",
        )

    def test_regra_temporal_nao_aplica_glosa(self):
        lancamento = self.criar_lancamento(
            "VIG-005",
            date(2025, 12, 1),
            date(2025, 12, 10),
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
