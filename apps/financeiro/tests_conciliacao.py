from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.financeiro.conciliacao import (
    StatusConciliacao,
    buscar_candidatos_lancamento,
    resumo_conciliacao_competencia,
)
from apps.financeiro.models import (
    ConciliacaoFinanceira,
    MovimentacaoFinanceira,
)
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos


class ConciliacaoFinanceiraTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="teste_conciliacao",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Teste Conciliacao",
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="CONC-001/2026",
            termo="Termo Conciliacao",
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipo="MENSAL",
            numtermo="CONC-001/2026",
        )

        self.competencia = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao,
                ano=2026,
                mes=1,
                data_inicial=date(2026, 1, 1),
                data_final=date(2026, 1, 31),
            )
        )

    def criar_movimentacao(
        self,
        tipo,
        valor,
        data_movimento,
    ):
        return MovimentacaoFinanceira.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=self.competencia,
            data=data_movimento,
            tipo=tipo,
            valor=Decimal(valor),
            descricao="Movimento teste",
            criado_por=self.usuario,
        )

    def criar_lancamento(
        self,
        numero,
        valor,
        data_pagamento,
    ):
        return Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            competencia=self.competencia,
            numero_lancamento=numero,
            data_documento=data_pagamento,
            data_pagamento=data_pagamento,
            descricao="Despesa teste",
            valor_documento=Decimal(valor),
            criado_por=self.usuario,
        )

    def test_repasse_nao_e_conciliavel_com_lancamento(self):
        movimento = self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.REPASSE,
            "100.00",
            date(2026, 1, 10),
        )

        resultado = buscar_candidatos_lancamento(
            movimento
        )

        self.assertEqual(
            resultado["status"],
            StatusConciliacao.NAO_APLICAVEL,
        )

    def test_encontra_correspondencia_exata(self):
        lancamento = self.criar_lancamento(
            "001",
            "250.00",
            date(2026, 1, 10),
        )

        movimento = self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "250.00",
            date(2026, 1, 10),
        )

        resultado = buscar_candidatos_lancamento(
            movimento
        )

        self.assertEqual(
            resultado["status"],
            StatusConciliacao.EXATO,
        )
        self.assertEqual(
            resultado["candidato"],
            lancamento,
        )

    def test_encontra_correspondencia_provavel(self):
        lancamento = self.criar_lancamento(
            "002",
            "300.00",
            date(2026, 1, 12),
        )

        movimento = self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "300.00",
            date(2026, 1, 10),
        )

        resultado = buscar_candidatos_lancamento(
            movimento
        )

        self.assertEqual(
            resultado["status"],
            StatusConciliacao.PROVAVEL,
        )
        self.assertEqual(
            resultado["candidato"],
            lancamento,
        )

    def test_valor_diferente_nao_concilia(self):
        self.criar_lancamento(
            "003",
            "500.00",
            date(2026, 1, 10),
        )

        movimento = self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "499.00",
            date(2026, 1, 10),
        )

        resultado = buscar_candidatos_lancamento(
            movimento
        )

        self.assertEqual(
            resultado["status"],
            StatusConciliacao.SEM_CORRESPONDENCIA,
        )
        self.assertIsNone(
            resultado["candidato"]
        )

    def test_multiplos_candidatos_sao_ambiguos(self):
        self.criar_lancamento(
            "004",
            "700.00",
            date(2026, 1, 10),
        )

        self.criar_lancamento(
            "005",
            "700.00",
            date(2026, 1, 10),
        )

        movimento = self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "700.00",
            date(2026, 1, 10),
        )

        resultado = buscar_candidatos_lancamento(
            movimento
        )

        self.assertEqual(
            resultado["status"],
            StatusConciliacao.AMBIGUO,
        )
        self.assertEqual(
            len(resultado["candidatos"]),
            2,
        )
        self.assertIsNone(
            resultado["candidato"]
        )

    def test_resumo_conciliacao_contabiliza_status(self):
        self.criar_lancamento(
            "010",
            "100.00",
            date(2026, 1, 10),
        )

        self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "100.00",
            date(2026, 1, 10),
        )

        self.criar_lancamento(
            "011",
            "200.00",
            date(2026, 1, 15),
        )

        self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "200.00",
            date(2026, 1, 13),
        )

        self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "999.00",
            date(2026, 1, 20),
        )

        resumo = resumo_conciliacao_competencia(
            self.competencia
        )

        self.assertEqual(resumo["total"], 3)
        self.assertEqual(resumo["exatos"], 1)
        self.assertEqual(resumo["provaveis"], 1)
        self.assertEqual(
            resumo["sem_correspondencia"],
            1,
        )
        self.assertEqual(resumo["ambiguos"], 0)
        self.assertEqual(resumo["conciliaveis"], 2)
        self.assertEqual(resumo["pendentes"], 1)

    def test_resumo_ignora_repasse(self):
        self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.REPASSE,
            "500.00",
            date(2026, 1, 10),
        )

        resumo = resumo_conciliacao_competencia(
            self.competencia
        )

        self.assertEqual(resumo["total"], 0)
        self.assertEqual(resumo["conciliaveis"], 0)
        self.assertEqual(resumo["pendentes"], 0)

    def test_resumo_informa_rotulo_do_status(self):
        self.criar_lancamento(
            "020",
            "150.00",
            date(2026, 1, 10),
        )

        self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "150.00",
            date(2026, 1, 10),
        )

        resumo = resumo_conciliacao_competencia(
            self.competencia
        )

        self.assertEqual(
            resumo["itens"][0]["status"],
            StatusConciliacao.EXATO,
        )

        self.assertEqual(
            resumo["itens"][0]["rotulo_status"],
            "Correspondencia exata",
        )

    def test_resumo_marca_colisao_de_movimentacoes_como_ambigua(self):
        self.criar_lancamento(
            "030",
            "250.00",
            date(2026, 1, 10),
        )

        self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "250.00",
            date(2026, 1, 10),
        )

        self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "250.00",
            date(2026, 1, 10),
        )

        resumo = resumo_conciliacao_competencia(
            self.competencia
        )

        self.assertEqual(
            resumo["total"],
            2,
        )

        self.assertEqual(
            resumo["exatos"],
            0,
        )

        self.assertEqual(
            resumo["ambiguos"],
            2,
        )

        self.assertEqual(
            resumo["conciliaveis"],
            0,
        )

        self.assertEqual(
            resumo["pendentes"],
            2,
        )

        for item in resumo["itens"]:
            self.assertEqual(
                item["status"],
                StatusConciliacao.AMBIGUO,
            )

    def test_resumo_informa_decisao_manual_confirmada(self):
        lancamento = self.criar_lancamento(
            "040",
            "250.00",
            date(2026, 1, 10),
        )

        movimento = self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "250.00",
            date(2026, 1, 10),
        )

        conciliacao = ConciliacaoFinanceira.objects.create(
            movimentacao=movimento,
            lancamento=lancamento,
            status=(
                ConciliacaoFinanceira.Status
                .CONFIRMADO
            ),
            decidido_por=self.usuario,
        )

        resumo = resumo_conciliacao_competencia(
            self.competencia
        )

        item = resumo["itens"][0]

        self.assertEqual(
            item["decisao_manual"],
            conciliacao,
        )

        self.assertEqual(
            item["status_manual"],
            ConciliacaoFinanceira.Status.CONFIRMADO,
        )

        self.assertEqual(
            resumo["confirmados"],
            1,
        )

        self.assertEqual(
            resumo["rejeitados"],
            0,
        )

        self.assertEqual(
            resumo["nao_analisados"],
            0,
        )

    def test_resumo_informa_decisao_manual_rejeitada(self):
        lancamento = self.criar_lancamento(
            "041",
            "300.00",
            date(2026, 1, 10),
        )

        movimento = self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "300.00",
            date(2026, 1, 10),
        )

        ConciliacaoFinanceira.objects.create(
            movimentacao=movimento,
            lancamento=lancamento,
            status=(
                ConciliacaoFinanceira.Status
                .REJEITADO
            ),
            decidido_por=self.usuario,
        )

        resumo = resumo_conciliacao_competencia(
            self.competencia
        )

        item = resumo["itens"][0]

        self.assertEqual(
            item["status_manual"],
            ConciliacaoFinanceira.Status.REJEITADO,
        )

        self.assertEqual(
            resumo["confirmados"],
            0,
        )

        self.assertEqual(
            resumo["rejeitados"],
            1,
        )

        self.assertEqual(
            resumo["nao_analisados"],
            0,
        )

    def test_resumo_informa_item_nao_analisado(self):
        self.criar_lancamento(
            "042",
            "180.00",
            date(2026, 1, 10),
        )

        self.criar_movimentacao(
            MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO,
            "180.00",
            date(2026, 1, 10),
        )

        resumo = resumo_conciliacao_competencia(
            self.competencia
        )

        item = resumo["itens"][0]

        self.assertIsNone(
            item["decisao_manual"]
        )

        self.assertIsNone(
            item["status_manual"]
        )

        self.assertEqual(
            resumo["confirmados"],
            0,
        )

        self.assertEqual(
            resumo["rejeitados"],
            0,
        )

        self.assertEqual(
            resumo["nao_analisados"],
            1,
        )
