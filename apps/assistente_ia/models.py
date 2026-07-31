from django.conf import settings
from django.db import models
from django.urls import reverse


class ProcessamentoAssistido(models.Model):
    class Status(models.TextChoices):
        CONCLUIDO = "concluido", "Concluído"
        REVISADO = "revisado", "Revisado"
        ERRO = "erro", "Com erro"

    class DecisaoRevisor(models.TextChoices):
        PENDENTE = "pendente", "Aguardando revisão"
        ACEITO = "aceito", "Sugestão aceita"
        ALTERADO = "alterado", "Sugestão alterada"
        REJEITADO = "rejeitado", "Sugestão rejeitada"

    documento = models.ForeignKey(
        "documentos.Documento",
        on_delete=models.CASCADE,
        related_name="processamentos_assistidos",
        verbose_name="Documento",
    )
    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="processamentos_assistidos",
        verbose_name="OSC / Empresa",
    )
    solicitado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processamentos_assistidos_solicitados",
        verbose_name="Solicitado por",
    )
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processamentos_assistidos_revisados",
        verbose_name="Revisado por",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONCLUIDO,
    )
    decisao_revisor = models.CharField(
        max_length=20,
        choices=DecisaoRevisor.choices,
        default=DecisaoRevisor.PENDENTE,
        verbose_name="Decisão do revisor",
    )
    resumo = models.TextField(blank=True)
    rascunho_inconformidade = models.TextField(blank=True)
    rascunho_diligencia = models.TextField(blank=True)
    rascunho_recomendacao = models.TextField(blank=True)
    observacoes_revisor = models.TextField(blank=True)
    ia_externa_utilizada = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    revisado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criado_em", "-id"]
        verbose_name = "Processamento assistido"
        verbose_name_plural = "Processamentos assistidos"

    def get_absolute_url(self):
        return reverse("assistente_ia_detalhe", kwargs={"pk": self.pk})

    def __str__(self):
        return f"Análise assistida #{self.pk} — {self.documento}"


class AchadoAssistido(models.Model):
    class Severidade(models.TextChoices):
        INFO = "info", "Informativo"
        ALERTA = "alerta", "Alerta"
        CRITICO = "critico", "Crítico"

    processamento = models.ForeignKey(
        ProcessamentoAssistido,
        on_delete=models.CASCADE,
        related_name="achados",
    )
    codigo = models.CharField(max_length=60)
    severidade = models.CharField(
        max_length=10,
        choices=Severidade.choices,
        default=Severidade.ALERTA,
    )
    titulo = models.CharField(max_length=180)
    descricao = models.TextField()
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "id"]
        verbose_name = "Achado assistido"
        verbose_name_plural = "Achados assistidos"

    def __str__(self):
        return self.titulo
