from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.core.permissoes_modulos import MODULOS


class ConfiguracaoDashboardUsuario(models.Model):

    class Estado(models.TextChoices):
        HERDAR = "herdar", "Herdar"
        MOSTRAR = "mostrar", "Mostrar"
        OCULTAR = "ocultar", "Ocultar"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="configuracoes_dashboard",
    )

    modulo = models.CharField(
        max_length=50,
    )

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.HERDAR,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "usuario",
                    "modulo",
                ],
                name="uniq_dashboard_usuario_modulo",
            ),
        ]

        ordering = [
            "usuario__username",
            "modulo",
        ]

    def clean(self):
        super().clean()

        if self.modulo not in MODULOS:
            raise ValidationError(
                {
                    "modulo": (
                        "O modulo informado nao existe "
                        "na matriz central do PGP."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.usuario} - "
            f"{self.modulo} - "
            f"{self.get_estado_display()}"
        )


class ConfiguracaoDashboardGrupo(models.Model):

    grupo = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="configuracoes_dashboard",
    )

    modulo = models.CharField(
        max_length=50,
    )

    exibir = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "grupo",
                    "modulo",
                ],
                name="uniq_dashboard_grupo_modulo",
            ),
        ]

        ordering = [
            "grupo__name",
            "modulo",
        ]

    def clean(self):
        super().clean()

        if self.modulo not in MODULOS:
            raise ValidationError(
                {
                    "modulo": (
                        "O modulo informado nao existe "
                        "na matriz central do PGP."
                    )
                }
            )

    def __str__(self):
        situacao = (
            "Exibir"
            if self.exibir
            else "Ocultar"
        )

        return (
            f"{self.grupo} - "
            f"{self.modulo} - "
            f"{situacao}"
        )
class ConfiguracaoDashboardWidgetUsuario(models.Model):

    class Estado(models.TextChoices):
        HERDAR = "herdar", "Herdar"
        MOSTRAR = "mostrar", "Mostrar"
        OCULTAR = "ocultar", "Ocultar"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="configuracoes_widgets_dashboard",
    )

    widget = models.CharField(
        max_length=60,
    )

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.HERDAR,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "widget"],
                name="uniq_dashboard_widget_usuario",
            ),
        ]

        ordering = [
            "usuario__username",
            "widget",
        ]

    def clean(self):
        super().clean()

        from apps.core.dashboard_widgets import WIDGETS_DASHBOARD

        if self.widget not in WIDGETS_DASHBOARD:
            raise ValidationError(
                {
                    "widget": (
                        "O bloco informado nao existe "
                        "no catalogo do Dashboard."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.usuario} - "
            f"{self.widget} - "
            f"{self.get_estado_display()}"
        )


class ConfiguracaoDashboardWidgetGrupo(models.Model):

    grupo = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="configuracoes_widgets_dashboard",
    )

    widget = models.CharField(
        max_length=60,
    )

    exibir = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["grupo", "widget"],
                name="uniq_dashboard_widget_grupo",
            ),
        ]

        ordering = [
            "grupo__name",
            "widget",
        ]

    def clean(self):
        super().clean()

        from apps.core.dashboard_widgets import WIDGETS_DASHBOARD

        if self.widget not in WIDGETS_DASHBOARD:
            raise ValidationError(
                {
                    "widget": (
                        "O bloco informado nao existe "
                        "no catalogo do Dashboard."
                    )
                }
            )

    def __str__(self):
        situacao = "Exibir" if self.exibir else "Ocultar"

        return (
            f"{self.grupo} - "
            f"{self.widget} - "
            f"{situacao}"
        )


class SequenciaPseudonimo(models.Model):

    class Tipo(models.TextChoices):
        COLABORADOR = "COL", "Colaborador"
        FORNECEDOR = "FOR", "Fornecedor"

    tipo = models.CharField(
        max_length=3,
        choices=Tipo.choices,
        unique=True,
    )

    ultimo_numero = models.PositiveBigIntegerField(
        default=0,
    )

    class Meta:
        verbose_name = "Sequencia de pseudonimo"
        verbose_name_plural = "Sequencias de pseudonimos"

    def __str__(self):
        return (
            f"{self.tipo}: "
            f"{self.ultimo_numero}"
        )

    @classmethod
    def proximo_codigo(cls, tipo):
        with transaction.atomic():
            sequencia = (
                cls.objects
                .select_for_update()
                .get(tipo=tipo)
            )

            sequencia.ultimo_numero += 1

            sequencia.save(
                update_fields=[
                    "ultimo_numero",
                ]
            )

            numero = sequencia.ultimo_numero

        return f"{tipo}-{numero:06d}"

