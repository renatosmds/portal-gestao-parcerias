from django.db import models
from django.urls import reverse


class Analise(models.Model):
    class Meta:
        ordering = ["concluida", "numtermo__termo", "numRA", "item"]
        verbose_name = "Análise"
        verbose_name_plural = "Análises"

    nomeOSC = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Nome da OSC",
    )
    numRA = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Nº Relatório de Auditoria (RA)",
    )
    item = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Item",
    )
    inconformidade = models.TextField(
        blank=True,
        null=True,
        verbose_name="Inconformidade",
    )
    recomendacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Recomendações",
    )
    posicaoSecretaria = models.TextField(
        blank=True,
        null=True,
        verbose_name="Posição da Secretaria",
    )
    status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Status",
    )
    concluida = models.BooleanField(
        default=False,
        verbose_name="Concluída",
    )
    criada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criada em",
    )
    atualizada_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizada em",
    )

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="analises_vinculadas",
        related_query_name="analise_vinculada",
        verbose_name="Empresa",
    )
    numtermo = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="analises_vinculadas",
        related_query_name="analise_vinculada",
        verbose_name="Termo",
    )
    prestacao = models.ForeignKey(
        "prestacao.Prestacao",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="analises_vinculadas",
        related_query_name="analise_vinculada",
        verbose_name="Prestação de contas",
    )

    def get_absolute_url(self):
        return reverse("detail_analise", kwargs={"pk": self.pk})

    def __str__(self):
        termo = str(self.numtermo) if self.numtermo_id else None
        identificacao = " - ".join(
            parte for parte in [termo, self.numRA, self.item] if parte
        )
        return identificacao or self.nomeOSC or f"Análise #{self.pk}"
