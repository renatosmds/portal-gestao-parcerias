from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Conciliacao(models.Model):
    class Situacao(models.TextChoices):
        INCOMPLETA = "incompleta", "Conciliação incompleta"
        COM_DIFERENCA = "com_diferenca", "Conciliação com diferença"
        FECHADA = "fechada", "Conciliação fechada"

    prestacao = models.OneToOneField(
        "prestacao.Prestacao", on_delete=models.CASCADE,
        related_name="conciliacao_bancaria", verbose_name="Prestação de contas"
    )
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))
    saldo_final_informado = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.INCOMPLETA)
    observacoes = models.TextField(blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="conciliacoes_criadas")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-atualizado_em"]
        verbose_name = "Conciliação bancária"
        verbose_name_plural = "Conciliações bancárias"

    @property
    def total_creditos(self):
        return self.movimentacoes.filter(tipo=Movimentacao.Tipo.CREDITO).aggregate(s=models.Sum("valor"))["s"] or Decimal("0.00")

    @property
    def total_debitos(self):
        return self.movimentacoes.filter(tipo=Movimentacao.Tipo.DEBITO).aggregate(s=models.Sum("valor"))["s"] or Decimal("0.00")

    @property
    def saldo_final_calculado(self):
        return self.saldo_inicial + self.total_creditos - self.total_debitos

    @property
    def diferenca(self):
        if self.saldo_final_informado is None:
            return None
        return self.saldo_final_informado - self.saldo_final_calculado

    def recalcular_situacao(self, salvar=True):
        pendentes = self.movimentacoes.exclude(situacao=Movimentacao.Situacao.CONCILIADA).exists()
        if self.saldo_final_informado is None or pendentes:
            nova = self.Situacao.INCOMPLETA
        elif abs(self.diferenca or Decimal("0.00")) > Decimal("0.01"):
            nova = self.Situacao.COM_DIFERENCA
        else:
            nova = self.Situacao.FECHADA
        self.situacao = nova
        if salvar:
            self.save(update_fields=["situacao", "atualizado_em"])
        return nova

    def get_absolute_url(self):
        return reverse("conciliacao_detalhe", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Conciliação — {self.prestacao}"


class ImportacaoExtrato(models.Model):
    class Situacao(models.TextChoices):
        PROCESSADA = "processada", "Processada"
        COM_ERROS = "com_erros", "Processada com erros"

    conciliacao = models.ForeignKey(Conciliacao, on_delete=models.CASCADE, related_name="importacoes")
    arquivo = models.FileField(upload_to="conciliacao/extratos/%Y/%m/")
    formato = models.CharField(max_length=10)
    total_linhas = models.PositiveIntegerField(default=0)
    total_importadas = models.PositiveIntegerField(default=0)
    total_erros = models.PositiveIntegerField(default=0)
    erros = models.JSONField(default=list, blank=True)
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.PROCESSADA)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]


class Movimentacao(models.Model):
    class Tipo(models.TextChoices):
        CREDITO = "credito", "Crédito"
        DEBITO = "debito", "Débito"

    class Categoria(models.TextChoices):
        REPASSE = "repasse", "Repasse"
        RENDIMENTO = "rendimento", "Rendimento"
        ESTORNO = "estorno", "Estorno"
        PAGAMENTO = "pagamento", "Pagamento"
        TARIFA = "tarifa", "Tarifa bancária"
        DEVOLUCAO = "devolucao", "Devolução"
        TRANSFERENCIA = "transferencia", "Transferência"
        OUTRO = "outro", "Outro"

    class Situacao(models.TextChoices):
        PENDENTE = "pendente", "Não conciliada"
        PARCIAL = "parcial", "Parcialmente conciliada"
        CONCILIADA = "conciliada", "Conciliada"
        IGNORADA = "ignorada", "Ignorada com justificativa"
        DIVERGENCIA = "divergencia", "Com divergência"

    conciliacao = models.ForeignKey(Conciliacao, on_delete=models.CASCADE, related_name="movimentacoes")
    importacao = models.ForeignKey(ImportacaoExtrato, on_delete=models.SET_NULL, null=True, blank=True, related_name="movimentacoes")
    data = models.DateField()
    descricao = models.CharField(max_length=255)
    documento = models.CharField(max_length=80, blank=True)
    favorecido = models.CharField(max_length=180, blank=True)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.OUTRO)
    valor = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    saldo_apos = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.PENDENTE)
    justificativa = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["data", "id"]
        constraints = [models.UniqueConstraint(fields=["conciliacao", "data", "descricao", "valor", "tipo"], name="movimentacao_bancaria_unica")]

    @property
    def valor_vinculado(self):
        return self.vinculos.aggregate(s=models.Sum("valor"))["s"] or Decimal("0.00")

    @property
    def valor_pendente(self):
        return max(self.valor - self.valor_vinculado, Decimal("0.00"))

    def atualizar_situacao(self):
        vinculado = self.valor_vinculado
        if self.situacao == self.Situacao.IGNORADA:
            return self.situacao
        if vinculado == Decimal("0.00"):
            nova = self.Situacao.PENDENTE
        elif vinculado < self.valor:
            nova = self.Situacao.PARCIAL
        elif abs(vinculado - self.valor) <= Decimal("0.01"):
            nova = self.Situacao.CONCILIADA
        else:
            nova = self.Situacao.DIVERGENCIA
        self.situacao = nova
        self.save(update_fields=["situacao"])
        self.conciliacao.recalcular_situacao()
        return nova

    def __str__(self):
        return f"{self.data:%d/%m/%Y} — {self.descricao}"


class VinculoConciliacao(models.Model):
    movimentacao = models.ForeignKey(Movimentacao, on_delete=models.CASCADE, related_name="vinculos")
    lancamento = models.ForeignKey("lancamentos.Lancamento", on_delete=models.PROTECT, related_name="vinculos_bancarios")
    valor = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    observacao = models.CharField(max_length=255, blank=True)
    confirmado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]
        constraints = [models.UniqueConstraint(fields=["movimentacao", "lancamento"], name="vinculo_movimentacao_lancamento_unico")]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.movimentacao.atualizar_situacao()

    def delete(self, *args, **kwargs):
        mov = self.movimentacao
        super().delete(*args, **kwargs)
        mov.atualizar_situacao()


class OcorrenciaConciliacao(models.Model):
    class Tipo(models.TextChoices):
        MOVIMENTO_SEM_LANCAMENTO = "mov_sem_lanc", "Movimentação sem lançamento"
        LANCAMENTO_SEM_MOVIMENTO = "lanc_sem_mov", "Lançamento sem movimentação"
        VALOR_DIVERGENTE = "valor_divergente", "Valor divergente"
        DUPLICIDADE = "duplicidade", "Possível pagamento em duplicidade"
        FORA_VIGENCIA = "fora_vigencia", "Pagamento fora da vigência"
        TARIFA = "tarifa", "Tarifa bancária"
        RENDIMENTO = "rendimento", "Rendimento não registrado"
        SALDO = "saldo", "Saldo final divergente"
        OUTRO = "outro", "Outro"

    class Situacao(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        JUSTIFICADA = "justificada", "Justificada"
        REGULARIZADA = "regularizada", "Regularizada"
        INCONFORMIDADE = "inconformidade", "Inconformidade"
        NAO_SE_APLICA = "nao_se_aplica", "Não se aplica"

    conciliacao = models.ForeignKey(Conciliacao, on_delete=models.CASCADE, related_name="ocorrencias")
    movimentacao = models.ForeignKey(Movimentacao, on_delete=models.CASCADE, null=True, blank=True, related_name="ocorrencias")
    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    descricao = models.TextField()
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.PENDENTE)
    justificativa = models.TextField(blank=True)
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["situacao", "-criado_em"]
