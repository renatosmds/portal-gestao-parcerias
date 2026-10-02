from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from apps.empresas.models import Empresa


class Departamento(models.Model):

    class Tipo(models.TextChoices):
        DEPARTAMENTO = "departamento", "Departamento"
        GABINETE = "gabinete", "Gabinete"
        ASSESSORIA = "assessoria", "Assessoria"
        SUBSECRETARIA = "subsecretaria", "Subsecretaria"
        SUPERINTENDENCIA = (
            "superintendencia",
            "Superintendencia",
        )
        DIRETORIA = "diretoria", "Diretoria"
        GERENCIA = "gerencia", "Gerencia"

    TIPOS_SUPERIORES_PERMITIDOS = {
        Tipo.GABINETE: {Tipo.DEPARTAMENTO},
        Tipo.ASSESSORIA: {Tipo.DEPARTAMENTO},
        Tipo.SUBSECRETARIA: {Tipo.DEPARTAMENTO},
        Tipo.SUPERINTENDENCIA: {
            Tipo.DEPARTAMENTO,
            Tipo.SUBSECRETARIA,
        },
        Tipo.DIRETORIA: {Tipo.SUPERINTENDENCIA},
        Tipo.GERENCIA: {Tipo.DIRETORIA},
    }

    class Meta:
        ordering = ["nome"]

    nome = models.CharField(max_length=150)

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
    )

    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
        default=Tipo.DEPARTAMENTO,
    )

    superior = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subunidades",
        verbose_name="Unidade superior",
    )

    def clean(self):
        super().clean()

        erros = {}

        if self.superior_id:
            if self.pk and self.superior_id == self.pk:
                erros["superior"] = (
                    "Uma unidade nao pode ser superior de si mesma."
                )

            if (
                self.empresa_id
                and self.superior.empresa_id != self.empresa_id
            ):
                erros["superior"] = (
                    "A unidade superior deve pertencer "
                    "a mesma empresa."
                )

            permitidos = self.TIPOS_SUPERIORES_PERMITIDOS.get(
                self.tipo
            )

            if (
                permitidos is not None
                and self.superior.tipo not in permitidos
            ):
                tipos = ", ".join(
                    sorted(
                        dict(self.Tipo.choices)[tipo]
                        for tipo in permitidos
                    )
                )

                erros["superior"] = (
                    "Para este tipo de unidade, a unidade "
                    f"superior deve ser: {tipos}."
                )

            if self.pk:
                ancestral = self.superior

                while ancestral:
                    if ancestral.pk == self.pk:
                        erros["superior"] = (
                            "A hierarquia informada cria "
                            "um ciclo entre as unidades."
                        )
                        break

                    ancestral = ancestral.superior

        elif self.tipo != self.Tipo.DEPARTAMENTO:
            erros["superior"] = (
                "Informe a unidade superior."
            )

        if erros:
            raise ValidationError(erros)

    def get_absolute_url(self):
        return reverse("list_departamentos")

    def __str__(self):
        return self.nome
