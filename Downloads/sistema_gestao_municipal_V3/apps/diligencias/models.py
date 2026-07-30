from django.conf import settings
from django.db import models
from django.urls import reverse


class Diligencia(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = "rascunho", "Rascunho"
        ENVIADA = "enviada", "Enviada à OSC"
        VISUALIZADA = "visualizada", "Visualizada"
        EM_RESPOSTA = "em_resposta", "Em resposta"
        RESPONDIDA = "respondida", "Respondida"
        REANALISE = "reanalise", "Em reanalise"
        ATENDIDA = "atendida", "Atendida"
        NAO_ATENDIDA = "nao_atendida", "Não atendida"
        CANCELADA = "cancelada", "Cancelada"

    class Prioridade(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        NORMAL = "normal", "Normal"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    assunto = models.CharField(max_length=180)
    descricao = models.TextField()
    fundamento = models.TextField(blank=True)
    prioridade = models.CharField(max_length=10, choices=Prioridade.choices, default=Prioridade.NORMAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RASCUNHO)
    prazo_resposta = models.DateField(null=True, blank=True)
    empresa = models.ForeignKey("empresas.Empresa", on_delete=models.PROTECT, null=True, blank=True, related_name="diligencias")
    prestacao = models.ForeignKey("prestacao.Prestacao", on_delete=models.PROTECT, null=True, blank=True, related_name="diligencias")
    lancamento = models.ForeignKey("lancamentos.Lancamento", on_delete=models.PROTECT, null=True, blank=True, related_name="diligencias")
    documento = models.ForeignKey("documentos.Documento", on_delete=models.PROTECT, null=True, blank=True, related_name="diligencias")
    funcionario = models.ForeignKey("funcionarios.Funcionario", on_delete=models.PROTECT, null=True, blank=True, related_name="diligencias")
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="diligencias_responsavel")
    criada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="diligencias_criadas")
    enviada_em = models.DateTimeField(null=True, blank=True)
    visualizada_em = models.DateTimeField(null=True, blank=True)
    encerrada_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "prazo_resposta", "-criado_em"]
        permissions = [("encerrar_diligencia", "Pode concluir diligência")]

    def get_absolute_url(self):
        return reverse("detail_diligencia", kwargs={"pk": self.pk})

    def __str__(self):
        return f"#{self.pk} - {self.assunto}"


class RespostaDiligencia(models.Model):
    diligencia = models.ForeignKey(Diligencia, on_delete=models.CASCADE, related_name="respostas")
    texto = models.TextField(verbose_name="Resposta / esclarecimento")
    anexo = models.FileField(upload_to="diligencias/respostas/%Y/%m/", blank=True, null=True)
    criada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]


class ComentarioInterno(models.Model):
    diligencia = models.ForeignKey(Diligencia, on_delete=models.CASCADE, related_name="comentarios_internos")
    texto = models.TextField()
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]


class Notificacao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notificacoes_pgp")
    diligencia = models.ForeignKey(Diligencia, on_delete=models.CASCADE, null=True, blank=True)
    titulo = models.CharField(max_length=180)
    mensagem = models.CharField(max_length=255, blank=True)
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
