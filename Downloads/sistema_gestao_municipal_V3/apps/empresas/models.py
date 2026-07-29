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

    conferencia3 = models.ForeignKey(
        "conferencia3.Conferencia3",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="empresas_legadas",
        verbose_name="Conferência legada",
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

    @property
    def totalOrdens(self):
        Conferencia3 = apps.get_model(
            "conferencia3",
            "Conferencia3",
        )

        return Conferencia3.objects.count()

    @property
    def ordensValor(self):
        Conferencia3 = apps.get_model(
            "conferencia3",
            "Conferencia3",
        )

        return self._somar_campo(
            Conferencia3,
            "valor",
        )

    @property
    def ordensConferir(self):
        Conferencia3 = apps.get_model(
            "conferencia3",
            "Conferencia3",
        )

        return Conferencia3.objects.filter(
            conferido=False,
            notificado=False,
            aprovado=False,
        ).count()

    @property
    def valorTotalExecucao(self):
        Conferencia3 = apps.get_model(
            "conferencia3",
            "Conferencia3",
        )

        return self._somar_campo(
            Conferencia3,
            "valorTotalExecucao",
        )

    # ------------------------------------------------------------------
    # CARD FINANCEIRO
    # ------------------------------------------------------------------

    @property
    def saldoRepasse(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "repasse",
        )

    @property
    def saldoDepositoOsc(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "depositoOsc",
        )

    @property
    def saldoRendimento(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "rendimento",
        )

    @property
    def saldoCreditoAutorizado(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "creditoAutorizado",
        )

    @property
    def saldoResgateAutomatico(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "resgateAutomatico",
        )

    @property
    def saldoEstorno(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "estorno",
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
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "aplicacao",
        )

    @property
    def saldoDebitoAutorizado(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "debitoAutorizado",
        )

    @property
    def saldoDespesaBancaria(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "despesaBancaria",
        )

    @property
    def saldoImpostoRenda(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "impostoRenda",
        )

    @property
    def saldoIof(self):
        Receitas = apps.get_model(
            "receitas",
            "Receitas",
        )

        return self._somar_campo(
            Receitas,
            "iof",
        )

    @property
    def despesaTotal(self):
        Conferencia3 = apps.get_model(
            "conferencia3",
            "Conferencia3",
        )

        saldo_despesas = self._somar_campo(
            Conferencia3,
            "valor",
        )

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
        Conferencia3 = apps.get_model(
            "conferencia3",
            "Conferencia3",
        )

        saldo_despesas = self._somar_campo(
            Conferencia3,
            "valor",
        )

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