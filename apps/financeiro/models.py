from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models



class ImportacaoOFX(models.Model):

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        related_name="importacoes_ofx",
    )

    termo = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        related_name="importacoes_ofx",
    )

    prestacao = models.ForeignKey(
        "prestacao.Prestacao",
        on_delete=models.PROTECT,
        related_name="importacoes_ofx",
        null=True,
        blank=True,
    )

    nome_arquivo = models.CharField(
        max_length=255,
    )

    hash_arquivo = models.CharField(
        max_length=64,
        db_index=True,
    )

    banco = models.CharField(
        max_length=20,
        blank=True,
    )

    conta_mascarada = models.CharField(
        max_length=64,
        blank=True,
    )

    tipo_conta = models.CharField(
        max_length=20,
        blank=True,
    )

    moeda = models.CharField(
        max_length=3,
        blank=True,
    )

    data_inicio = models.DateField()

    data_fim = models.DateField()

    saldo_informado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )

    data_saldo = models.DateField(
        null=True,
        blank=True,
    )

    quantidade_movimentos = models.PositiveIntegerField(
        default=0,
    )

    importado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="importacoes_ofx",
    )

    importado_em = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = (
            "-importado_em",
            "-id",
        )

        verbose_name = "Importacao OFX"
        verbose_name_plural = "Importacoes OFX"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "empresa",
                    "termo",
                    "hash_arquivo",
                ],
                name=(
                    "financeiro_ofx_"
                    "arquivo_unico_por_termo"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.nome_arquivo} - "
            f"{self.data_inicio} a "
            f"{self.data_fim}"
        )

    def clean(self):
        erros = {}

        if (
            self.termo_id
            and self.empresa_id
            and self.termo.empresa_id
            != self.empresa_id
        ):
            erros["termo"] = (
                "O termo informado nao pertence "
                "a empresa selecionada."
            )

        if self.prestacao_id:
            if (
                self.empresa_id
                and self.prestacao.empresa_id
                != self.empresa_id
            ):
                erros["prestacao"] = (
                    "A prestacao informada nao pertence "
                    "a empresa selecionada."
                )

            elif (
                self.prestacao.termo_id
                != self.termo_id
            ):
                erros["prestacao"] = (
                    "A prestacao informada nao pertence "
                    "ao termo selecionado."
                )

        if (
            self.data_inicio
            and self.data_fim
            and self.data_fim < self.data_inicio
        ):
            erros["data_fim"] = (
                "A data final nao pode ser anterior "
                "a data inicial."
            )

        if erros:
            raise ValidationError(erros)


class MovimentacaoFinanceira(models.Model):

    importacao_ofx = models.ForeignKey(
        "financeiro.ImportacaoOFX",
        on_delete=models.PROTECT,
        related_name="movimentos",
        null=True,
        blank=True,
    )

    movimento_relacionado = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="movimentos_relacionados",
        null=True,
        blank=True,
    )

    ordem_ofx = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    tipo_ofx = models.CharField(
        max_length=20,
        blank=True,
    )

    data_hora_ofx = models.DateTimeField(
        null=True,
        blank=True,
    )

    valor_ofx = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )

    fitid = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
    )

    hash_movimento = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
    )

    checknum = models.CharField(
        max_length=255,
        blank=True,
    )

    memo_ofx = models.CharField(
        max_length=255,
        blank=True,
    )


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
        constraints = [
            models.CheckConstraint(
                condition=models.Q(valor__gt=0),
                name="financeiro_valor_maior_que_zero",
            ),
            models.UniqueConstraint(
                fields=[
                    "empresa",
                    "termo",
                    "hash_movimento",
                ],
                condition=~models.Q(
                    hash_movimento=""
                ),
                name=(
                    "financeiro_ofx_"
                    "movimento_unico_por_termo"
                ),
            ),
        ]

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
            if (
                self.empresa_id
                and self.prestacao.empresa_id != self.empresa_id
            ):
                erros["prestacao"] = (
                    "A prestacao informada nao pertence "
                    "a empresa selecionada."
                )
            elif self.prestacao.termo_id != self.termo_id:
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


class ConciliacaoFinanceira(models.Model):

    class Status(models.TextChoices):
        CONFIRMADO = (
            "confirmado",
            "Confirmado",
        )
        REJEITADO = (
            "rejeitado",
            "Rejeitado",
        )

    movimentacao = models.OneToOneField(
        "financeiro.MovimentacaoFinanceira",
        on_delete=models.CASCADE,
        related_name="conciliacao_manual",
    )

    lancamento = models.ForeignKey(
        "lancamentos.Lancamento",
        on_delete=models.PROTECT,
        related_name="conciliacoes_financeiras",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
    )

    decidido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="conciliacoes_financeiras_decididas",
    )

    decidido_em = models.DateTimeField(
        auto_now=True,
    )

    observacao = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = (
            "-decidido_em",
            "-id",
        )

        verbose_name = (
            "Conciliacao financeira"
        )

        verbose_name_plural = (
            "Conciliacoes financeiras"
        )

        constraints = [
            models.UniqueConstraint(
                fields=["lancamento"],
                condition=models.Q(
                    status="confirmado"
                ),
                name=(
                    "financeiro_lancamento_"
                    "confirmado_unico"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.movimentacao} -> "
            f"{self.lancamento} "
            f"({self.get_status_display()})"
        )

    def clean(self):
        erros = {}

        movimentacao = self.movimentacao
        lancamento = self.lancamento

        if (
            movimentacao.tipo
            != MovimentacaoFinanceira.Tipo.DEBITO_AUTORIZADO
        ):
            erros["movimentacao"] = (
                "Somente debitos autorizados podem "
                "ser conciliados com lancamentos."
            )

        if (
            movimentacao.empresa_id
            != lancamento.empresa_id
        ):
            erros["lancamento"] = (
                "O lancamento nao pertence "
                "a mesma empresa da movimentacao."
            )

        elif (
            movimentacao.termo_id
            != lancamento.termo_id
        ):
            erros["lancamento"] = (
                "O lancamento nao pertence "
                "ao mesmo termo da movimentacao."
            )

        elif (
            movimentacao.prestacao_id
            != lancamento.prestacao_id
        ):
            erros["lancamento"] = (
                "O lancamento nao pertence "
                "a mesma prestacao da movimentacao."
            )

        elif (
            movimentacao.competencia_id
            != lancamento.competencia_id
        ):
            erros["lancamento"] = (
                "O lancamento nao pertence "
                "a mesma competencia da movimentacao."
            )

        if erros:
            raise ValidationError(erros)
