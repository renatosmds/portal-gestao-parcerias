from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Lancamento(models.Model):
    class Situacao(models.TextChoices):
        NAO_ANALISADO = "nao_analisado", "Não analisado"
        REGULAR = "regular", "Regular"
        RESSALVA = "ressalva", "Aprovado com ressalva"
        REPROVADO = "reprovado", "Reprovado"
        GLOSADO = "glosado", "Glosado"

    class TipoDocumento(models.TextChoices):
        NFE = "nfe", "NF-e"
        NFCE = "nfce", "NFC-e"
        NFS_E = "nfse", "NFS-e"
        RECIBO = "recibo", "Recibo"
        BOLETO = "boleto", "Boleto"
        FOLHA = "folha", "Folha de pagamento"
        OUTRO = "outro", "Outro"

    class Meta:
        ordering = ["-data_documento", "-id"]
        verbose_name = "Lançamento"
        verbose_name_plural = "Lançamentos"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "numero_lancamento"],
                name="lancamento_unico_por_empresa",
            )
        ]

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        related_name="lancamentos",
        related_query_name="lancamento",
        verbose_name="Empresa",
    )
    termo = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="lancamentos",
        related_query_name="lancamento",
        verbose_name="Termo",
    )
    prestacao = models.ForeignKey(
        "prestacao.Prestacao",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="lancamentos",
        related_query_name="lancamento",
        verbose_name="Prestação de contas",
    )
    fornecedor = models.ForeignKey(
        "fornecedores.Fornecedores",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="lancamentos",
        related_query_name="lancamento",
        verbose_name="Fornecedor",
    )
    analise = models.ForeignKey(
        "analise.Analise",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lancamentos",
        related_query_name="lancamento",
        verbose_name="Análise técnica",
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lancamentos_criados",
        verbose_name="Criado por",
    )

    numero_lancamento = models.CharField(
        max_length=30,
        verbose_name="Nº do lançamento",
    )
    tipo_documento = models.CharField(
        max_length=20,
        choices=TipoDocumento.choices,
        default=TipoDocumento.NFE,
        verbose_name="Tipo de documento",
    )
    numero_documento = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Nº do documento fiscal",
    )
    chave_acesso = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Chave de acesso",
    )
    data_documento = models.DateField(
        verbose_name="Data do documento",
    )
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do pagamento",
    )
    descricao = models.CharField(
        max_length=255,
        verbose_name="Descrição da despesa",
    )
    valor_documento = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor do documento",
    )
    valor_glosa = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor da glosa",
    )
    situacao = models.CharField(
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.NAO_ANALISADO,
        verbose_name="Situação",
    )
    atestado = models.BooleanField(
        default=False,
        verbose_name="Documento atestado",
    )
    justificativa = models.TextField(
        blank=True,
        verbose_name="Justificativa / inconformidade",
    )
    recomendacao = models.TextField(
        blank=True,
        verbose_name="Recomendação",
    )
    documento = models.FileField(
        upload_to="lancamentos/documentos/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Documento comprobatório",
    )
    comprovante_pagamento = models.FileField(
        upload_to="lancamentos/pagamentos/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Comprovante de pagamento",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    @property
    def valor_aprovado(self):
        return max(self.valor_documento - self.valor_glosa, Decimal("0.00"))

    def get_absolute_url(self):
        return reverse("detail_lancamento", kwargs={"pk": self.pk})

    def __str__(self):
        return self.numero_lancamento or f"Lançamento #{self.pk}"
