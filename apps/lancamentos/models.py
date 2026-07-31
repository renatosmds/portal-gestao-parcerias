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


    class TipoGlosa(models.TextChoices):
        NENHUMA = "nenhuma", "Sem glosa"
        PARCIAL = "parcial", "Glosa parcial"
        GLOBAL = "global", "Glosa global"

    class MotivoGlosa(models.TextChoices):
        SEM_COMPROVACAO = "sem_comprovacao", "Despesa sem comprovação"
        DOCUMENTO_IRREGULAR = "documento_irregular", "Documento fiscal irregular"
        FORA_VIGENCIA = "fora_vigencia", "Despesa fora da vigência"
        NAO_PREVISTA = "nao_prevista", "Despesa não prevista no plano de trabalho"
        DUPLICIDADE = "duplicidade", "Pagamento em duplicidade"
        SEM_PAGAMENTO = "sem_pagamento", "Ausência de comprovante de pagamento"
        INCOMPATIVEL = "incompativel", "Despesa incompatível com o objeto"
        OUTRO = "outro", "Outro motivo"

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

    tipo_glosa = models.CharField(max_length=12, choices=TipoGlosa.choices, default=TipoGlosa.NENHUMA, verbose_name="Tipo de glosa")
    motivo_glosa = models.CharField(max_length=30, choices=MotivoGlosa.choices, blank=True, verbose_name="Motivo da glosa")
    fundamentacao_glosa = models.TextField(blank=True, verbose_name="Fundamentação da glosa")
    glosa_registrada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="glosas_registradas")
    glosa_registrada_em = models.DateTimeField(null=True, blank=True)

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


class HistoricoGlosa(models.Model):
    lancamento = models.ForeignKey(Lancamento, on_delete=models.CASCADE, related_name="historico_glosas")
    tipo_anterior = models.CharField(max_length=12, blank=True)
    tipo_novo = models.CharField(max_length=12, choices=Lancamento.TipoGlosa.choices)
    valor_anterior = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    valor_novo = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    motivo = models.CharField(max_length=30, blank=True)
    fundamentacao = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-criado_em"]
