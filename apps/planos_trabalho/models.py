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

    versao_anterior = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="versoes_subsequentes",
        verbose_name="Versão anterior",
    )

    data_eficacia = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de eficácia da versão",
    )

    instrumento_alteracao = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Instrumento da alteração",
        help_text=(
            "Ex.: Termo Aditivo nº 01, autorização de remanejamento "
            "ou outro instrumento aplicável."
        ),
    )

    justificativa_alteracao = models.TextField(
        blank=True,
        verbose_name="Justificativa da alteração",
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
            ),
            models.UniqueConstraint(
                fields=[
                    "termo",
                ],
                condition=models.Q(
                    situacao="vigente"
                ),
                name="uniq_plano_vigente_por_termo",
            ),
        ]

        verbose_name = "Plano de Trabalho"
        verbose_name_plural = "Planos de Trabalho"

    @property
    def inicio_eficacia(self):
        return (
            self.data_eficacia
            or self.inicio_vigencia
        )

    def aplicavel_em(self, data_referencia):
        if not data_referencia:
            return False

        if self.situacao in {
            self.Situacao.RASCUNHO,
            self.Situacao.CANCELADO,
        }:
            return False

        inicio = self.inicio_eficacia

        if (
            inicio
            and data_referencia < inicio
        ):
            return False

        if (
            self.fim_vigencia
            and data_referencia > self.fim_vigencia
        ):
            return False

        return True

    def clean(self):
        super().clean()

        erros = {}

        if (
            self.inicio_vigencia
            and self.fim_vigencia
            and self.fim_vigencia < self.inicio_vigencia
        ):
            erros["fim_vigencia"] = (
                "O término da vigência não pode ser "
                "anterior ao início."
            )

        if (
            self.versao_anterior_id
            and self.pk
            and self.versao_anterior_id == self.pk
        ):
            erros["versao_anterior"] = (
                "Uma versão não pode apontar para si própria."
            )

        if self.versao_anterior:
            if (
                self.termo_id
                and self.versao_anterior.termo_id
                != self.termo_id
            ):
                erros["versao_anterior"] = (
                    "A versão anterior deve pertencer "
                    "ao mesmo Termo."
                )

            if (
                self.versao
                <= self.versao_anterior.versao
            ):
                erros["versao"] = (
                    "A nova versão deve possuir número "
                    "superior ao da versão anterior."
                )

        if (
            self.origem != self.Origem.INICIAL
            and not self.versao_anterior
        ):
            erros["versao_anterior"] = (
                "Versões decorrentes de alteração devem "
                "indicar a versão anterior."
            )

        if (
            self.origem == self.Origem.INICIAL
            and self.versao_anterior
        ):
            erros["origem"] = (
                "Uma versão vinculada a outra versão não "
                "pode ser classificada como Plano inicial."
            )

        if erros:
            raise ValidationError(erros)

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


