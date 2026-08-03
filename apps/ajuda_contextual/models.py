from django.conf import settings
from django.db import models


class AjudaContextual(models.Model):
    modulo = models.CharField(max_length=100, db_index=True)
    formulario = models.CharField(max_length=150, blank=True)
    campo = models.CharField(max_length=150, db_index=True)
    chave = models.SlugField(max_length=250, unique=True)
    titulo = models.CharField(max_length=200)
    ajuda_curta = models.CharField(max_length=300, blank=True)
    what = models.TextField("O que é", blank=True)
    why = models.TextField("Por que", blank=True)
    who = models.TextField("Quem", blank=True)
    when = models.TextField("Quando", blank=True)
    where = models.TextField("Onde", blank=True)
    how = models.TextField("Como", blank=True)
    how_much = models.TextField("Quanto / impacto", blank=True)
    exemplo = models.TextField(blank=True)
    atencao = models.TextField(blank=True)
    referencia = models.CharField(max_length=300, blank=True)
    publica = models.BooleanField(default=False, help_text="Permite consulta sem autenticação em páginas públicas.")
    ativo = models.BooleanField(default=True)
    versao = models.PositiveIntegerField(default=1)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ajudas_contextuais_criadas")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ajuda contextual"
        verbose_name_plural = "Ajudas contextuais"
        ordering = ["modulo", "formulario", "campo"]
        indexes = [models.Index(fields=["modulo", "campo", "ativo"])]

    def __str__(self):
        return f"{self.modulo} — {self.titulo}"

    def as_dict(self):
        return {
            "chave": self.chave, "titulo": self.titulo, "ajuda_curta": self.ajuda_curta,
            "what": self.what, "why": self.why, "who": self.who, "when": self.when,
            "where": self.where, "how": self.how, "how_much": self.how_much,
            "exemplo": self.exemplo, "atencao": self.atencao, "referencia": self.referencia,
            "versao": self.versao,
        }


class AcessoAjuda(models.Model):
    ajuda = models.ForeignKey(AjudaContextual, on_delete=models.CASCADE, related_name="acessos")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    caminho = models.CharField(max_length=300, blank=True)
    util = models.BooleanField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Acesso à ajuda"
        verbose_name_plural = "Acessos às ajudas"
        ordering = ["-criado_em"]
