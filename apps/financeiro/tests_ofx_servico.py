from pathlib import Path
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.financeiro.models import (
    ImportacaoOFX,
    MovimentacaoFinanceira,
)
from apps.financeiro.servicos_ofx import importar_ofx
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


class ImportacaoOFXServicoTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.empresa = Empresa.objects.create(
            nome="OSC Teste OFX",
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="OFX-001/2026",
            termo="Termo Teste OFX",
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="MENSAL",
            numtermo="OFX-001/2026",
        )

        self.usuario = User.objects.create_user(
            username="teste_ofx",
            password="teste123",
        )

        self.fixture = (
            Path(__file__).resolve().parent
            / "tests"
            / "fixtures"
            / "ofx"
            / "extrato_referencia_julho_2026.ofx"
        )

    def importar(self):
        return importar_ofx(
            self.fixture,
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            usuario=self.usuario,
        )

    def test_importa_arquivo_com_103_movimentos(self):
        importacao, criada = self.importar()

        self.assertTrue(criada)

        self.assertEqual(
            ImportacaoOFX.objects.count(),
            1,
        )

        self.assertEqual(
            MovimentacaoFinanceira.objects.count(),
            103,
        )

        self.assertEqual(
            importacao.quantidade_movimentos,
            103,
        )

    def test_metadados_da_importacao(self):
        importacao, _ = self.importar()

        self.assertEqual(
            importacao.banco,
            "0104",
        )

        self.assertEqual(
            importacao.moeda,
            "BRL",
        )

        self.assertEqual(
            importacao.tipo_conta,
            "CHECKING",
        )

        self.assertEqual(
            str(importacao.data_inicio),
            "2026-07-01",
        )

        self.assertEqual(
            str(importacao.data_fim),
            "2026-07-31",
        )

        self.assertEqual(
            importacao.saldo_informado,
            Decimal("1135860.09"),
        )

        self.assertEqual(
            str(importacao.data_saldo),
            "2026-08-11",
        )

    def test_conta_e_armazenada_mascarada(self):
        importacao, _ = self.importar()

        self.assertNotEqual(
            importacao.conta_mascarada,
            "0000000000000",
        )

        self.assertTrue(
            importacao.conta_mascarada.endswith(
                "0000"
            )
        )

        self.assertIn(
            "*",
            importacao.conta_mascarada,
        )

    def test_primeiro_movimento_preserva_dados_ofx(self):
        self.importar()

        movimento = (
            MovimentacaoFinanceira.objects
            .get(ordem_ofx=1)
        )

        self.assertEqual(
            movimento.data.isoformat(),
            "2026-07-01",
        )

        self.assertEqual(
            movimento.valor,
            Decimal("4562.61"),
        )

        self.assertEqual(
            movimento.valor_ofx,
            Decimal("-4562.61"),
        )

        self.assertEqual(
            movimento.tipo_ofx,
            "DEBIT",
        )

        self.assertEqual(
            movimento.fitid,
            "11035",
        )

        self.assertEqual(
            movimento.checknum,
            "11035",
        )

        self.assertEqual(
            movimento.memo_ofx,
            "ENVIO TEV",
        )

        self.assertEqual(
            movimento.tipo,
            MovimentacaoFinanceira
            .Tipo
            .DEBITO_AUTORIZADO,
        )

    def test_resgate_automatico_e_classificado(self):
        self.importar()

        quantidade = (
            MovimentacaoFinanceira.objects
            .filter(
                tipo=(
                    MovimentacaoFinanceira
                    .Tipo
                    .RESGATE_AUTOMATICO
                )
            )
            .count()
        )

        self.assertEqual(
            quantidade,
            17,
        )

    def test_estornos_e_devolucao_sao_classificados(self):
        self.importar()

        quantidade = (
            MovimentacaoFinanceira.objects
            .filter(
                tipo=(
                    MovimentacaoFinanceira
                    .Tipo
                    .ESTORNO
                )
            )
            .count()
        )

        self.assertEqual(
            quantidade,
            3,
        )

    def test_fitid_zero_pode_repetir(self):
        self.importar()

        quantidade = (
            MovimentacaoFinanceira.objects
            .filter(
                fitid="0",
            )
            .count()
        )

        self.assertEqual(
            quantidade,
            17,
        )

    def test_fitid_repetido_nao_elimina_movimentos(self):
        self.importar()

        quantidade = (
            MovimentacaoFinanceira.objects
            .filter(
                fitid="11046",
            )
            .count()
        )

        self.assertEqual(
            quantidade,
            2,
        )

    def test_reimportacao_do_mesmo_arquivo_e_idempotente(self):
        primeira, criada_1 = self.importar()
        segunda, criada_2 = self.importar()

        self.assertTrue(
            criada_1
        )

        self.assertFalse(
            criada_2
        )

        self.assertEqual(
            primeira.pk,
            segunda.pk,
        )

        self.assertEqual(
            ImportacaoOFX.objects.count(),
            1,
        )

        self.assertEqual(
            MovimentacaoFinanceira.objects.count(),
            103,
        )

    def test_todos_movimentos_ficam_vinculados_a_importacao(self):
        importacao, _ = self.importar()

        self.assertEqual(
            importacao.movimentos.count(),
            103,
        )

        self.assertFalse(
            MovimentacaoFinanceira.objects
            .filter(
                importacao_ofx__isnull=True,
            )
            .exists()
        )

    def test_todos_movimentos_recebem_hash(self):
        self.importar()

        sem_hash = (
            MovimentacaoFinanceira.objects
            .filter(hash_movimento="")
            .count()
        )

        self.assertEqual(
            sem_hash,
            0,
        )

    def test_hashes_sao_unicos_no_extrato(self):
        self.importar()

        hashes = list(
            MovimentacaoFinanceira.objects
            .values_list(
                "hash_movimento",
                flat=True,
            )
        )

        self.assertEqual(
            len(hashes),
            len(set(hashes)),
        )

    def test_hash_e_deterministico(self):
        self.importar()

        primeiro = (
            MovimentacaoFinanceira.objects
            .get(ordem_ofx=1)
        )

        hash_primeira_importacao = (
            primeiro.hash_movimento
        )

        MovimentacaoFinanceira.objects.all().delete()

        ImportacaoOFX.objects.all().delete()

        self.importar()

        segundo = (
            MovimentacaoFinanceira.objects
            .get(ordem_ofx=1)
        )

        self.assertEqual(
            segundo.hash_movimento,
            hash_primeira_importacao,
        )


    def test_arquivo_diferente_com_mesmos_movimentos_nao_duplica(self):
        from tempfile import TemporaryDirectory

        primeira, criada_1 = self.importar()

        self.assertTrue(
            criada_1
        )

        self.assertEqual(
            MovimentacaoFinanceira.objects.count(),
            103,
        )

        with TemporaryDirectory() as pasta:
            origem = self.fixture

            destino = (
                Path(pasta)
                / "extrato_reexportado.ofx"
            )

            dados = origem.read_bytes()

            texto = dados.decode("cp1252")

            texto = texto.replace(
                "NEWFILEUID:NONE",
                "NEWFILEUID:ARQUIVO-REEXPORTADO",
                1,
            )

            destino.write_bytes(
                texto.encode("cp1252")
            )

            segunda, criada_2 = importar_ofx(
                destino,
                empresa=self.empresa,
                termo=self.termo,
                prestacao=self.prestacao,
                usuario=self.usuario,
            )

        self.assertTrue(
            criada_2
        )

        self.assertNotEqual(
            primeira.hash_arquivo,
            segunda.hash_arquivo,
        )

        self.assertEqual(
            ImportacaoOFX.objects.count(),
            2,
        )

        self.assertEqual(
            MovimentacaoFinanceira.objects.count(),
            103,
        )

        self.assertEqual(
            segunda.movimentos.count(),
            0,
        )


    def test_estorno_ted_relaciona_debito_original(self):
        self.importar()

        estorno = (
            MovimentacaoFinanceira.objects
            .get(
                fitid="427325",
                tipo=(
                    MovimentacaoFinanceira
                    .Tipo
                    .ESTORNO
                ),
            )
        )

        self.assertIsNotNone(
            estorno.movimento_relacionado
        )

        original = (
            estorno.movimento_relacionado
        )

        self.assertEqual(
            original.fitid,
            "427325",
        )

        self.assertEqual(
            original.tipo_ofx,
            "DEBIT",
        )

        self.assertEqual(
            original.valor_ofx,
            Decimal("-1647.92"),
        )

        self.assertEqual(
            estorno.valor_ofx,
            Decimal("1647.92"),
        )

    def test_devolucao_ted_relaciona_debito_original(self):
        self.importar()

        devolucao = (
            MovimentacaoFinanceira.objects
            .get(
                fitid="667361",
                tipo=(
                    MovimentacaoFinanceira
                    .Tipo
                    .ESTORNO
                ),
            )
        )

        self.assertIsNotNone(
            devolucao.movimento_relacionado
        )

        original = (
            devolucao.movimento_relacionado
        )

        self.assertEqual(
            original.fitid,
            "667361",
        )

        self.assertEqual(
            original.valor_ofx,
            Decimal("-1650.00"),
        )

        self.assertEqual(
            devolucao.valor_ofx,
            Decimal("1650.00"),
        )

    def test_resgate_automatico_nao_recebe_movimento_relacionado(self):
        self.importar()

        resgates = (
            MovimentacaoFinanceira.objects
            .filter(
                tipo=(
                    MovimentacaoFinanceira
                    .Tipo
                    .RESGATE_AUTOMATICO
                )
            )
        )

        self.assertEqual(
            resgates.count(),
            17,
        )

        self.assertFalse(
            resgates.filter(
                movimento_relacionado__isnull=False
            ).exists()
        )
