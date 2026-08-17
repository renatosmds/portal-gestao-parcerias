from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class PlanoTrabalho(models.Model):

    class Situacao(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        VIGENTE = "vigente", "Vigente"
        SUBSTITUIDO = "substituido", "Substituído"
        CANCELADO = "cancelado", "Cancelado"

    class Origem(models.TextChoices):
        INICIAL = "inicial", "Plano inicial"
        ADITIVO = "aditivo", "Termo aditivo"
        REMANEJAMENTO = "remanejamento", "Remanejamento"
        OUTRA = "outra", "Outra alteração"

    termo = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        related_name="planos_trabalho_estruturados",
        verbose_name="Termo",
    )

    versao = models.PositiveIntegerField(
        default=1,
        verbose_name="Versão",
    )

    titulo = models.CharField(
        max_length=180,
        blank=True,
        verbose_name="Título",
    )

    origem = models.CharField(
        max_length=20,
        choices=Origem.choices,
        default=Origem.INICIAL,
        verbose_name="Origem da versão",
    )

    situacao = models.CharField(
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.RASCUNHO,
        verbose_name="Situação",
    )

    inicio_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Início da vigência",
    )

    fim_vigencia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fim da vigência",
    )

    data_aprovacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de aprovação",
    )

    arquivo = models.FileField(
        upload_to="planos_trabalho/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Arquivo da versão",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "termo",
            "-versao",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "termo",
                    "versao",
                ],
                name="uniq_plano_termo_versao",
            )
        ]

        verbose_name = "Plano de Trabalho"
        verbose_name_plural = "Planos de Trabalho"

    def clean(self):
        super().clean()

        if (
            self.inicio_vigencia
            and self.fim_vigencia
            and self.fim_vigencia < self.inicio_vigencia
        ):
            raise ValidationError(
                {
                    "fim_vigencia": (
                        "O término da vigência não pode ser "
                        "anterior ao início."
                    )
                }
            )

    def __str__(self):
        termo = (
            getattr(self.termo, "numtermo", None)
            or getattr(self.termo, "termo", None)
            or str(self.termo_id)
        )

        return f"{termo} - versão {self.versao}"


class ItemPlanoTrabalho(models.Model):

    plano = models.ForeignKey(
        PlanoTrabalho,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Plano de Trabalho",
    )

    codigo = models.CharField(
        max_length=50,
        verbose_name="Código do item",
    )

    rubrica_nivel_1 = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Rubrica nível 1",
    )

    rubrica_nivel_2 = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Rubrica nível 2",
    )

    rubrica_nivel_3 = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Rubrica nível 3",
    )

    descricao = models.CharField(
        max_length=255,
        verbose_name="Descrição",
    )

    unidade = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Unidade",
    )

    quantidade_prevista = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.0000")
            )
        ],
        verbose_name="Quantidade prevista",
    )

    valor_unitario_previsto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ],
        verbose_name="Valor unitário previsto",
    )

    valor_total_previsto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.00")
            )
        ],
        verbose_name="Valor total previsto",
    )

    inicio_execucao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Início previsto da execução",
    )

    fim_execucao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fim previsto da execução",
    )

    meta = models.ForeignKey(
        "metas.MetaExecucao",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="itens_plano_trabalho",
        verbose_name="Meta relacionada",
    )

    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
    )

    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "plano",
            "codigo",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "plano",
                    "codigo",
                ],
                name="uniq_item_codigo_por_plano",
            )
        ]

        verbose_name = "Item do Plano de Trabalho"
        verbose_name_plural = "Itens do Plano de Trabalho"

    @property
    def valor_calculado(self):
        if (
            self.quantidade_prevista is None
            or self.valor_unitario_previsto is None
        ):
            return None

        return (
            self.quantidade_prevista
            * self.valor_unitario_previsto
        ).quantize(
            Decimal("0.01")
        )

    def clean(self):
        super().clean()

        if (
            self.inicio_execucao
            and self.fim_execucao
            and self.fim_execucao < self.inicio_execucao
        ):
            raise ValidationError(
                {
                    "fim_execucao": (
                        "O término da execução não pode ser "
                        "anterior ao início."
                    )
                }
            )

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"
