from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class MovimentacaoFinanceira(models.Model):

    class Tipo(models.TextChoices):
        REPASSE = "repasse", "Repasse"
        DEPOSITO_OSC = "deposito_osc", "Deposito OSC"
        RENDIMENTO = "rendimento", "Rendimento"
        CREDITO_AUTORIZADO = (
            "credito_autorizado",
            "Credito autorizado",
        )
        RESGATE_AUTOMATICO = (
            "resgate_automatico",
            "Resgate automatico",
        )
        ESTORNO = "estorno", "Estorno"
        APLICACAO = "aplicacao", "Aplicacao financeira"
        DEBITO_AUTORIZADO = (
            "debito_autorizado",
            "Debito autorizado",
        )
        DESPESA_BANCARIA = (
            "despesa_bancaria",
            "Despesa bancaria",
        )
        IMPOSTO_RENDA = (
            "imposto_renda",
            "Imposto de renda",
        )
        IOF = "iof", "IOF"

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        related_name="movimentacoes_financeiras",
    )

    termo = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        related_name="movimentacoes_financeiras",
    )

    prestacao = models.ForeignKey(
        "prestacao.Prestacao",
        on_delete=models.PROTECT,
        related_name="movimentacoes_financeiras",
        null=True,
        blank=True,
    )

    competencia = models.ForeignKey(
        "prestacao.CompetenciaPrestacao",
        on_delete=models.PROTECT,
        related_name="movimentacoes_financeiras",
        null=True,
        blank=True,
    )

    data = models.DateField()

    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
        db_index=True,
    )

    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    descricao = models.CharField(
        max_length=255,
        blank=True,
    )

    documento = models.FileField(
        upload_to="financeiro/",
        null=True,
        blank=True,
    )

    observacao = models.TextField(
        blank=True,
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="movimentacoes_financeiras_criadas",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = (
            "data",
            "id",
        )
        verbose_name = "Movimentacao financeira"
        verbose_name_plural = "Movimentacoes financeiras"

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.data} - "
            f"{self.valor}"
        )

    def clean(self):
        erros = {}

        if self.valor is not None and self.valor <= 0:
            erros["valor"] = (
                "Informe um valor maior que zero. "
                "O tipo da movimentacao define sua natureza."
            )

        if (
            self.termo_id
            and self.empresa_id
            and self.termo.empresa_id != self.empresa_id
        ):
            erros["termo"] = (
                "O termo informado nao pertence "
                "a empresa selecionada."
            )

        if self.prestacao_id:
            if self.prestacao.termo_id != self.termo_id:
                erros["prestacao"] = (
                    "A prestacao informada nao pertence "
                    "ao termo selecionado."
                )

        if self.competencia_id:
            if self.competencia.prestacao_id != self.prestacao_id:
                erros["competencia"] = (
                    "A competencia informada nao pertence "
                    "a prestacao selecionada."
                )

        if erros:
            raise ValidationError(erros)
