from django.apps import apps
from django.db import models
from django.db.models import Sum
from django.urls import reverse


class Empresa(models.Model):
    class Meta:
        ordering = ["nome"]
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    nome = models.CharField(
        max_length=100,
        help_text="Nome da empresa",
    )

    # Relacionamentos legados
    receitas = models.ForeignKey(
        "receitas.Receitas",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="empresas_legadas",
        verbose_name="Receita legada",
    )

    curso = models.ForeignKey(
        "curso.Curso",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="empresas_legadas",
        verbose_name="Curso legado",
    )

    termos = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="empresas_legadas",
        related_query_name="empresa_legada",
        verbose_name="Termo legado",
    )

    prestacao = models.ForeignKey(
        "prestacao.Prestacao",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="empresas_legadas",
        related_query_name="empresa_legada",
        verbose_name="Prestação legada",
    )


    parcerias = models.ForeignKey(
        "parcerias.Parcerias",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="empresas_legadas",
        related_query_name="empresa_legada",
        verbose_name="Parceria legada",
    )

    # ------------------------------------------------------------------
    # FUNÇÕES INTERNAS PARA SOMAS
    # ------------------------------------------------------------------

    @staticmethod
    def _somar_campo(modelo, campo):
        """
        Soma um campo de determinado model.

        Retorna zero quando não existirem registros ou quando todos
        os valores estiverem vazios.
        """
        resultado = modelo.objects.aggregate(
            total=Sum(campo, default=0)
        )

        return resultado.get("total") or 0

    def _somar_termos(self, campo):
        """
        Soma somente os termos pertencentes à empresa atual.
        """
        Termos = apps.get_model("termos", "Termos")

        resultado = Termos.objects.filter(
            empresa=self
        ).aggregate(
            total=Sum(campo, default=0)
        )

        return resultado.get("total") or 0

    # ------------------------------------------------------------------
    # CARD EMPREGADOS
    # ------------------------------------------------------------------

    @property
    def total_funcionarios(self):
        return self.funcionario_set.count()

    @property
    def total_funcionarios_ferias(self):
        return self.funcionario_set.filter(
            de_ferias=True
        ).count()

    @property
    def total_funcionarios_doc_pendente(self):
        return (
            self.funcionario_set
            .filter(documentos_legados__isnull=True)
            .distinct()
            .count()
        )

    @property
    def total_funcionarios_doc_ok(self):
        return (
            self.funcionario_set
            .filter(documentos_legados__isnull=False)
            .distinct()
            .count()
        )

    # ------------------------------------------------------------------
    # CARD EXECUÇÃO
    # ------------------------------------------------------------------

    def _somar_lancamentos(self, campo):
        """
        Soma um campo apenas dos lancamentos pertencentes
        a esta empresa.
        """
        resultado = self.lancamentos.aggregate(
            total=Sum(campo, default=0)
        )

        return resultado.get("total") or 0

    def _somar_movimentacoes_financeiras(self, tipo):
        MovimentacaoFinanceira = apps.get_model(
            "financeiro",
            "MovimentacaoFinanceira",
        )

        resultado = (
            MovimentacaoFinanceira.objects
            .filter(
                empresa=self,
                tipo=tipo,
            )
            .aggregate(
                total=Sum(
                    "valor",
                    default=0,
                )
            )
        )

        return resultado.get("total") or 0

    @property
    def totalOrdens(self):
        return self.lancamentos.count()

    @property
    def ordensValor(self):
        return self._somar_lancamentos(
            "valor_documento"
        )

    @property
    def ordensConferir(self):
        return self.lancamentos.filter(
            situacao="nao_analisado"
        ).count()

    @property
    def valorTotalExecucao(self):
        return self._somar_lancamentos(
            "valor_documento"
        )

    # ------------------------------------------------------------------
    # CARD FINANCEIRO
    # ------------------------------------------------------------------

    @property
    def saldoRepasse(self):
        return self._somar_movimentacoes_financeiras(
            "repasse"
        )

    @property
    def saldoDepositoOsc(self):
        return self._somar_movimentacoes_financeiras(
            "deposito_osc"
        )

    @property
    def saldoRendimento(self):
        return self._somar_movimentacoes_financeiras(
            "rendimento"
        )

    @property
    def saldoCreditoAutorizado(self):
        return self._somar_movimentacoes_financeiras(
            "credito_autorizado"
        )

    @property
    def saldoResgateAutomatico(self):
        return self._somar_movimentacoes_financeiras(
            "resgate_automatico"
        )

    @property
    def saldoEstorno(self):
        return self._somar_movimentacoes_financeiras(
            "estorno"
        )

    @property
    def receitaTotal(self):
        return (
            self.saldoRepasse
            + self.saldoDepositoOsc
            + self.saldoRendimento
            + self.saldoCreditoAutorizado
            + self.saldoEstorno
        )

    @property
    def saldoAplicacao(self):
        return self._somar_movimentacoes_financeiras(
            "aplicacao"
        )

    @property
    def saldoDebitoAutorizado(self):
        return self._somar_movimentacoes_financeiras(
            "debito_autorizado"
        )

    @property
    def saldoDespesaBancaria(self):
        return self._somar_movimentacoes_financeiras(
            "despesa_bancaria"
        )

    @property
    def saldoImpostoRenda(self):
        return self._somar_movimentacoes_financeiras(
            "imposto_renda"
        )

    @property
    def saldoIof(self):
        return self._somar_movimentacoes_financeiras(
            "iof"
        )

    @property
    def despesaTotal(self):
        saldo_despesas = self.ordensValor

        return (
            self.saldoDebitoAutorizado
            + self.saldoDespesaBancaria
            + self.saldoImpostoRenda
            + self.saldoIof
            + saldo_despesas
        )

    @property
    def saldoContaAplicacao(self):
        return (
            self.saldoAplicacao
            - self.saldoResgateAutomatico
        )

    @property
    def saldoFinanceiro(self):
        saldo_despesas = self.ordensValor

        total_entradas = (
            self.saldoRepasse
            + self.saldoDepositoOsc
            + self.saldoRendimento
            + self.saldoCreditoAutorizado
            + self.saldoResgateAutomatico
            + self.saldoEstorno
        )

        total_saidas = (
            self.saldoAplicacao
            + self.saldoDebitoAutorizado
            + self.saldoDespesaBancaria
            + self.saldoImpostoRenda
            + self.saldoIof
            + saldo_despesas
        )

        return total_entradas - total_saidas

    # ------------------------------------------------------------------
    # CARD TERMOS
    # ------------------------------------------------------------------

    @property
    def valorglobaltotal(self):
        return self._somar_termos(
            "valorglobal"
        )

    @property
    def valorRepasseTotal(self):
        return self._somar_termos(
            "valorrepasse"
        )

    @property
    def valorSaldoTotal(self):
        return self._somar_termos(
            "valorsaldo"
        )

    # ------------------------------------------------------------------
    # CARD AUDITORIAS / PARCERIAS
    # ------------------------------------------------------------------

    @property
    def auditoriasQtd(self):
        Parcerias = apps.get_model(
            "parcerias",
            "Parcerias",
        )

        return Parcerias.objects.filter(
            empresa=self
        ).count()

    @property
    def auditoriasAbertas(self):
        Parcerias = apps.get_model(
            "parcerias",
            "Parcerias",
        )

        return Parcerias.objects.filter(
            empresa=self,
            concluido=False,
        ).count()

    # ------------------------------------------------------------------
    # REPRESENTAÇÃO E URL
    # ------------------------------------------------------------------

    def __str__(self):
        return self.nome or f"Empresa #{self.pk}"

    def get_absolute_url(self):
        return reverse("home")