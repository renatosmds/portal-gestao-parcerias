# coding: utf-8
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.urls import reverse

from apps.core.models import SequenciaPseudonimo
from apps.core.documentos_fiscais import (
    documento_cpf_normalizado,
    documento_cnpj_normalizado,
)


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
    documento_normalizado = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        unique=True,
        editable=False,
        verbose_name="Documento normalizado",
    )
    codigo_pseudonimo = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        editable=False,
        verbose_name="Código pseudonimizado",
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
        "empresas.Empresa",
        on_delete=models.PROTECT,
        related_name="fornecedores",
        blank=True,
        null=True,
    )

    def _validar_identidade_pseudonima(self):
        precisa_validar = (
            not self.codigo_pseudonimo
            or self.documento_normalizado is not None
        )

        if not precisa_validar:
            # Registro legado preservado ate saneamento posterior.
            return

        tipo = (self.tipo or "").strip().lower()

        try:
            if tipo == "cpf":
                documento = documento_cpf_normalizado(
                    self.numero
                )
            elif tipo == "cnpj":
                documento = documento_cnpj_normalizado(
                    self.numero
                )
            else:
                raise ValueError(
                    "Tipo de documento invalido."
                )
        except ValueError as exc:
            raise ValidationError(
                {
                    "numero": (
                        "CPF/CNPJ obrigatorio e valido para "
                        "identificacao pseudonimizada."
                    )
                }
            ) from exc

        if self.pk and self.codigo_pseudonimo:
            anterior = (
                type(self).objects
                .filter(pk=self.pk)
                .values_list(
                    "documento_normalizado",
                    flat=True,
                )
                .first()
            )

            if anterior and anterior != documento:
                raise ValidationError(
                    {
                        "numero": (
                            "O CPF/CNPJ associado ao codigo "
                            "pseudonimizado nao pode ser alterado."
                        )
                    }
                )

        duplicado = (
            type(self).objects
            .exclude(pk=self.pk)
            .filter(
                documento_normalizado=documento
            )
            .exists()
        )

        if duplicado:
            raise ValidationError(
                {
                    "numero": (
                        "Este CPF/CNPJ ja possui um fornecedor "
                        "pseudonimizado."
                    )
                }
            )

        self.documento_normalizado = documento

    def clean(self):
        super().clean()
        self._validar_identidade_pseudonima()

    def save(self, *args, **kwargs):
        self._validar_identidade_pseudonima()

        with transaction.atomic():
            if not self.codigo_pseudonimo:
                self.codigo_pseudonimo = (
                    SequenciaPseudonimo.proximo_codigo(
                        SequenciaPseudonimo.Tipo.FORNECEDOR
                    )
                )

            return super().save(*args, **kwargs)

    def __str__(self):
        return (
                self.credor
                or self.razao
                or self.fantasia
                or f"Fornecedor #{self.pk}"
        )

    def get_absolute_url(self):
        return reverse("detail_fornecedor", kwargs={"pk": self.pk})
