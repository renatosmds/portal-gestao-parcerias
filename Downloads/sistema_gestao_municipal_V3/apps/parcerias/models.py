# coding: utf-8
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Parcerias(models.Model):
    class Meta:
        ordering = ["numtermo__termo", "nomeOSC"]
        verbose_name = "Parceria"
        verbose_name_plural = "Parcerias"

    nomeOSC = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="OSC",
    )
    fileTC = models.FileField(
        upload_to="parcerias_photos",
        null=True,
        blank=True,
        verbose_name="TC",
    )
    numRA = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name="RA",
    )
    numOficioRA = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Ofício - RA",
    )
    fileRA = models.FileField(
        upload_to="parcerias_photos",
        null=True,
        blank=True,
        verbose_name="Relatório Auditoria (RA)",
    )
    fileOficioRA = models.FileField(
        upload_to="parcerias_photos",
        null=True,
        blank=True,
        verbose_name="Ofício RA",
    )
    dtRaSMDS = models.DateField(
        null=True,
        blank=True,
        verbose_name="Entrada RA",
    )
    respRA = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        verbose_name="Resposta RA",
    )
    numRE = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name="RE",
    )
    numOficioRE = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Ofício - RE",
    )
    fileRE = models.FileField(
        upload_to="parcerias_photos",
        null=True,
        blank=True,
        verbose_name="Relatório Efetividade (RE)",
    )
    fileOficioRE = models.FileField(
        upload_to="parcerias_photos",
        null=True,
        blank=True,
        verbose_name="Ofício RE",
    )
    dtReSMDS = models.DateField(
        null=True,
        blank=True,
        verbose_name="Entrada RE",
    )
    respRE = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        verbose_name="Resposta RE",
    )
    fileRRE = models.FileField(
        upload_to="parcerias_photos",
        null=True,
        blank=True,
        verbose_name="Resposta RE",
    )
    prazoFinal = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name="Prazo Final",
    )
    status = models.TextField(
        null=True,
        blank=True,
        verbose_name="Status",
    )
    prazoDecorrido = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name="Prazo Decorrido",
    )
    prazoRestante = models.CharField(
        max_length=8,
        null=True,
        blank=True,
        verbose_name="Prazo Restante",
    )
    historico = models.TextField(
        null=True,
        blank=True,
        verbose_name="Histórico",
    )
    concluido = models.BooleanField(
        default=False,
        verbose_name="Concluído",
    )
    photo = models.ImageField(
        upload_to="parcerias_photos",
        null=True,
        blank=True,
    )

    # Campo legado preservado. Novos cadastros não criam usuário automaticamente.
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    numtermo = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="parcerias_vinculadas",
        verbose_name="Termo",
    )
    credor = models.ForeignKey(
        "fornecedores.Fornecedores",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="parcerias_vinculadas",
        verbose_name="Fornecedor/credor",
    )
    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="parcerias_vinculadas",
        verbose_name="Empresa",
    )

    def __str__(self):
        termo = getattr(self.numtermo, "termo", None) or getattr(
            self.numtermo,
            "numtermo",
            None,
        )
        return termo or self.nomeOSC or f"Parceria #{self.pk}"

    def get_absolute_url(self):
        return reverse("detail_parceria", kwargs={"pk": self.pk})
