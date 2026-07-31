from django.conf import settings
from django.db import models
from django.urls import reverse


class Documento(models.Model):
    class Tipo(models.TextChoices):
        NOTA_FISCAL = "nota_fiscal", "Nota fiscal"
        COMPROVANTE = "comprovante", "Comprovante de pagamento"
        ATESTO = "atesto", "Atesto"
        EXTRATO = "extrato", "Extrato bancário"
        CONTRATO = "contrato", "Contrato / termo"
        FOLHA = "folha", "Folha de pagamento"
        GUIA = "guia", "Guia de recolhimento"
        OUTRO = "outro", "Outro"

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EM_CONFERENCIA = "em_conferencia", "Em conferência"
        CONFERIDO = "conferido", "Conferido"
        COM_PENDENCIA = "com_pendencia", "Com pendência"
        REPROVADO = "reprovado", "Reprovado"

    class Meta:
        ordering = ["status", "-atualizado_em", "-id"]
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    descricao = models.CharField(max_length=150, verbose_name="Descrição")
    arquivo = models.FileField(
        upload_to="documentos/%Y/%m/",
        verbose_name="Arquivo",
    )

    pertence = models.ForeignKey(
        "funcionarios.Funcionario",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="documentos_legados",
        verbose_name="Funcionário (legado)",
    )
    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="documentos",
        related_query_name="documento",
        verbose_name="Empresa",
    )
    termo = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="documentos_vinculados",
        related_query_name="documento_vinculado",
        verbose_name="Termo",
    )
    prestacao = models.ForeignKey(
        "prestacao.Prestacao",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="documentos_vinculados",
        related_query_name="documento_vinculado",
        verbose_name="Prestação de contas",
    )
    lancamento = models.ForeignKey(
        "lancamentos.Lancamento",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documentos_vinculados",
        related_query_name="documento_vinculado",
        verbose_name="Lançamento",
    )
    conferido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_conferidos",
        verbose_name="Conferido por",
    )

    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
        default=Tipo.OUTRO,
        verbose_name="Tipo de documento",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDENTE,
        verbose_name="Status da conferência",
    )
    numero_documento = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Número do documento",
    )
    data_documento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do documento",
    )
    documento_legivel = models.BooleanField(
        default=False,
        verbose_name="Documento legível",
    )
    dados_compativeis = models.BooleanField(
        default=False,
        verbose_name="Dados compatíveis",
    )
    vigencia_valida = models.BooleanField(
        default=False,
        verbose_name="Vigência válida",
    )
    pagamento_comprovado = models.BooleanField(
        default=False,
        verbose_name="Pagamento comprovado",
    )
    atesto_valido = models.BooleanField(
        default=False,
        verbose_name="Atesto válido",
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações da conferência",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    conferido_em = models.DateTimeField(null=True, blank=True)

    @property
    def total_itens_conferidos(self):
        return sum(
            [
                self.documento_legivel,
                self.dados_compativeis,
                self.vigencia_valida,
                self.pagamento_comprovado,
                self.atesto_valido,
            ]
        )

    @property
    def percentual_conferencia(self):
        return int((self.total_itens_conferidos / 5) * 100)

    def get_absolute_url(self):
        return reverse("detail_documento", kwargs={"pk": self.pk})

    def __str__(self):
        return self.descricao or f"Documento #{self.pk}"
