from django.conf import settings
from django.db import models


class ArtigoConhecimento(models.Model):
    CATEGORIAS = [
        ("acesso", "Acesso e usuários"),
        ("termos", "Termos e parcerias"),
        ("prestacao", "Prestação de contas"),
        ("documentos", "Documentos e lançamentos"),
        ("analise", "Análise, diligência e glosa"),
        ("conciliacao", "Conciliação bancária"),
        ("transparencia", "Transparência"),
        ("tecnico", "Questões técnicas"),
    ]
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    resumo = models.CharField(max_length=300, blank=True)
    conteudo = models.TextField()
    publico = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "titulo"]
        verbose_name = "Artigo da base de conhecimento"
        verbose_name_plural = "Artigos da base de conhecimento"

    def __str__(self):
        return self.titulo


class ChamadoSuporte(models.Model):
    PRIORIDADES = [("baixa", "Baixa"), ("normal", "Normal"), ("alta", "Alta"), ("critica", "Crítica")]
    SITUACOES = [
        ("aberto", "Aberto"),
        ("em_analise", "Em análise"),
        ("aguardando_usuario", "Aguardando usuário"),
        ("resolvido", "Resolvido"),
        ("encerrado", "Encerrado"),
    ]
    CATEGORIAS = ArtigoConhecimento.CATEGORIAS

    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chamados_suporte")
    assunto = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    prioridade = models.CharField(max_length=10, choices=PRIORIDADES, default="normal")
    situacao = models.CharField(max_length=25, choices=SITUACOES, default="aberto")
    pagina_origem = models.CharField(max_length=500, blank=True)
    anexo = models.FileField(upload_to="suporte/%Y/%m/", blank=True, null=True)
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="chamados_atendidos")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    encerrado_em = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-atualizado_em"]
        verbose_name = "Chamado de suporte"
        verbose_name_plural = "Chamados de suporte"

    def __str__(self):
        return f"#{self.pk} — {self.assunto}"


class InteracaoChamado(models.Model):
    chamado = models.ForeignKey(ChamadoSuporte, on_delete=models.CASCADE, related_name="interacoes")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensagem = models.TextField()
    interno = models.BooleanField(default=False, help_text="Visível somente para a equipe interna.")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]
        verbose_name = "Interação do chamado"
        verbose_name_plural = "Interações dos chamados"

    def __str__(self):
        return f"Interação #{self.pk} do chamado #{self.chamado_id}"
