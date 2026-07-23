# coding: utf-8
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from apps.empresas.models import Empresa


class Fornecedores(models.Model):
    class Meta:
        ordering = ["credor"]
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    TIPO_CHOICES = (
        ("cnpj", "CNPJ"),
        ("cpf", "CPF"),
    )

    PESSOA_CHOICES = (
        ("física", "Física"),
        ("jurídica", "Jurídica"),
    )

    credor = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Nome do credor",
    )
    pessoa = models.CharField(
        max_length=50,
        choices=PESSOA_CHOICES,
        blank=True,
        null=True,
        verbose_name="Pessoa",
    )
    razao = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Razão social",
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        blank=True,
        null=True,
        verbose_name="CPF/CNPJ",
    )
    numero = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número",
    )
    fantasia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nome fantasia",
    )
    endereco = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Endereço",
    )
    bairro = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Bairro",
    )
    cep = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="CEP",
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cidade",
    )
    estado = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Estado",
    )
    email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="E-mail",
    )
    telefone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Telefone",
    )
    iestadual = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Inscrição estadual",
    )
    imunicipal = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Inscrição municipal",
    )

    # Campo legado preservado para não quebrar registros antigos.
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="fornecedores",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.credor or self.razao or self.fantasia or f"Fornecedor #{self.pk}"

    def get_absolute_url(self):
        return reverse("detail_fornecedor", kwargs={"pk": self.pk})
