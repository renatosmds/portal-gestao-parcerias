from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class MetaExecucao(models.Model):
    class Unidade(models.TextChoices):
        NUMERO = "numero", "Número"
        PERCENTUAL = "percentual", "Percentual"
        MOEDA = "moeda", "Valor em reais"
        PESSOAS = "pessoas", "Pessoas atendidas"
        HORAS = "horas", "Horas"

    class Situacao(models.TextChoices):
        NAO_INICIADA = "nao_iniciada", "Não iniciada"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        ATINGIDA = "atingida", "Atingida"
        PARCIAL = "parcial", "Parcialmente atingida"
        NAO_ATINGIDA = "nao_atingida", "Não atingida"
        SUSPENSA = "suspensa", "Suspensa"

    prestacao = models.ForeignKey(
        "prestacao.Prestacao", on_delete=models.CASCADE, related_name="metas_execucao"
    )
    codigo = models.CharField(max_length=30, blank=True)
    titulo = models.CharField(max_length=180)
    descricao = models.TextField(blank=True)
    unidade = models.CharField(max_length=20, choices=Unidade.choices, default=Unidade.NUMERO)
    valor_previsto = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    valor_realizado = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0"))])
    inicio = models.DateField(null=True, blank=True)
    fim = models.DateField(null=True, blank=True)
    situacao = models.CharField(max_length=24, choices=Situacao.choices, default=Situacao.NAO_INICIADA)
    justificativa = models.TextField(blank=True)
    responsavel = models.CharField(max_length=150, blank=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="metas_criadas")
    atualizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="metas_atualizadas")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["prestacao", "codigo", "titulo"]
        verbose_name = "Meta de execução"
        verbose_name_plural = "Metas de execução"

    @property
    def percentual_execucao(self):
        if not self.valor_previsto:
            return Decimal("0")
        return min((self.valor_realizado / self.valor_previsto) * 100, Decimal("999.99"))

    def get_absolute_url(self):
        return reverse("metas_detalhe", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.codigo + ' — ' if self.codigo else ''}{self.titulo}"


class AtualizacaoMeta(models.Model):
    meta = models.ForeignKey(MetaExecucao, on_delete=models.CASCADE, related_name="atualizacoes")
    valor_realizado = models.DecimalField(max_digits=14, decimal_places=2)
    situacao = models.CharField(max_length=24, choices=MetaExecucao.Situacao.choices)
    observacao = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Atualização da meta"
        verbose_name_plural = "Atualizações das metas"
