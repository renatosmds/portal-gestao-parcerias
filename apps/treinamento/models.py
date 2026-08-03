from django.conf import settings
from django.db import models


class ProgressoTreinamento(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progressos_treinamento")
    modulo = models.CharField(max_length=80)
    concluido = models.BooleanField(default=False)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("usuario", "modulo")
        ordering = ["modulo"]
        verbose_name = "Progresso de treinamento"
        verbose_name_plural = "Progressos de treinamento"

    def __str__(self):
        return f"{self.usuario} — {self.modulo}"


class PreferenciaTour(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preferencia_tour")
    tour_concluido = models.BooleanField(default=False)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preferência de tour"
        verbose_name_plural = "Preferências de tour"
