from django.conf import settings
from django.db import models


class Importacao(models.Model):
    class Tipo(models.TextChoices):
        OSC = "osc", "OSCs / Empresas"
        TERMO = "termo", "Termos"
        PRESTACAO = "prestacao", "Prestações de contas"
        LANCAMENTO = "lancamento", "Lançamentos"

    class Situacao(models.TextChoices):
        VALIDACAO = "validacao", "Em validação"
        CONFIRMADA = "confirmada", "Confirmada"
        PARCIAL = "parcial", "Parcialmente aplicada"
        CANCELADA = "cancelada", "Cancelada"
        ERRO = "erro", "Com erro"

    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    arquivo_nome = models.CharField(max_length=255)
    sistema_origem = models.CharField(max_length=80, blank=True, default="Arquivo externo")
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.VALIDACAO)
    cabecalhos = models.JSONField(default=list, blank=True)
    linhas = models.JSONField(default=list, blank=True)
    erros = models.JSONField(default=list, blank=True)
    total_lido = models.PositiveIntegerField(default=0)
    total_novos = models.PositiveIntegerField(default=0)
    total_atualizados = models.PositiveIntegerField(default=0)
    total_duplicados = models.PositiveIntegerField(default=0)
    total_erros = models.PositiveIntegerField(default=0)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    confirmado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Importação"
        verbose_name_plural = "Importações"

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.arquivo_nome}"
