from django.conf import settings
from django.db import models


class PublicacaoParceria(models.Model):
    termo = models.OneToOneField(
        "termos.Termos",
        on_delete=models.CASCADE,
        related_name="publicacao_transparencia",
        verbose_name="Termo",
    )
    publicada = models.BooleanField(default=False, verbose_name="Publicada")
    orgao_responsavel = models.CharField(max_length=150, blank=True, verbose_name="Órgão responsável")
    resumo_publico = models.TextField(blank=True, verbose_name="Resumo público")
    publicada_em = models.DateTimeField(null=True, blank=True, verbose_name="Publicada em")
    publicada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parcerias_publicadas",
        verbose_name="Publicada por",
    )
    motivo_restricao = models.TextField(blank=True, verbose_name="Motivo da restrição")
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-publicada", "termo__numtermo", "termo__termo"]
        verbose_name = "Publicação de parceria"
        verbose_name_plural = "Publicações de parcerias"

    def __str__(self):
        return f"{self.termo} — {'Pública' if self.publicada else 'Não publicada'}"


class PublicacaoDocumento(models.Model):
    class Classificacao(models.TextChoices):
        PUBLICO = "publico", "Público"
        INTERNO = "interno", "Interno"
        RESTRITO = "restrito", "Restrito"
        DADO_PESSOAL = "dado_pessoal", "Dado pessoal"
        DADO_SENSIVEL = "dado_sensivel", "Dado pessoal sensível"

    documento = models.OneToOneField(
        "documentos.Documento",
        on_delete=models.CASCADE,
        related_name="publicacao_transparencia",
        verbose_name="Documento",
    )
    classificacao = models.CharField(
        max_length=24,
        choices=Classificacao.choices,
        default=Classificacao.INTERNO,
        verbose_name="Classificação",
    )
    publicado = models.BooleanField(default=False, verbose_name="Publicado")
    titulo_publico = models.CharField(max_length=180, blank=True, verbose_name="Título público")
    descricao_publica = models.TextField(blank=True, verbose_name="Descrição pública")
    motivo_restricao = models.TextField(blank=True, verbose_name="Motivo da restrição")
    publicado_em = models.DateTimeField(null=True, blank=True, verbose_name="Publicado em")
    publicado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_publicados",
        verbose_name="Publicado por",
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-publicado", "documento__descricao"]
        verbose_name = "Publicação de documento"
        verbose_name_plural = "Publicações de documentos"

    @property
    def disponivel_publicamente(self):
        return self.publicado and self.classificacao == self.Classificacao.PUBLICO

    def __str__(self):
        return self.titulo_publico or self.documento.descricao


class HistoricoPublicacao(models.Model):
    class Acao(models.TextChoices):
        PUBLICAR = "publicar", "Publicar"
        RETIRAR = "retirar", "Retirar da transparência"
        RECLASSIFICAR = "reclassificar", "Reclassificar"
        ALTERAR = "alterar", "Alterar dados públicos"

    termo = models.ForeignKey(
        "termos.Termos",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="historicos_publicacao",
    )
    documento = models.ForeignKey(
        "documentos.Documento",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="historicos_publicacao",
    )
    acao = models.CharField(max_length=24, choices=Acao.choices)
    detalhes = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Histórico de publicação"
        verbose_name_plural = "Históricos de publicação"

    def __str__(self):
        alvo = self.termo or self.documento or "Item"
        return f"{alvo} — {self.get_acao_display()}"
