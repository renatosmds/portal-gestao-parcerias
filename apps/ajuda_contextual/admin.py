from django.contrib import admin
from .models import AjudaContextual, AcessoAjuda


@admin.register(AjudaContextual)
class AjudaContextualAdmin(admin.ModelAdmin):
    list_display = ("titulo", "modulo", "campo", "ativo", "publica", "versao", "atualizado_em")
    list_filter = ("modulo", "ativo", "publica")
    search_fields = ("titulo", "chave", "campo", "ajuda_curta", "what", "how")
    readonly_fields = ("criado_em", "atualizado_em")
    fieldsets = (
        ("Identificação", {"fields": ("modulo", "formulario", "campo", "chave", "titulo", "ajuda_curta")}),
        ("5W2H", {"fields": ("what", "why", "who", "when", "where", "how", "how_much")}),
        ("Complementos", {"fields": ("exemplo", "atencao", "referencia")}),
        ("Controle", {"fields": ("publica", "ativo", "versao", "criado_por", "criado_em", "atualizado_em")}),
    )


@admin.register(AcessoAjuda)
class AcessoAjudaAdmin(admin.ModelAdmin):
    list_display = ("ajuda", "usuario", "util", "criado_em")
    list_filter = ("util", "criado_em")
    search_fields = ("ajuda__titulo", "usuario__username", "caminho")
    readonly_fields = ("ajuda", "usuario", "caminho", "util", "criado_em")
