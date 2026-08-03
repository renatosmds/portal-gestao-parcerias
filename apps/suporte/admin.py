from django.contrib import admin

from .models import ArtigoConhecimento, ChamadoSuporte, InteracaoChamado


@admin.register(ArtigoConhecimento)
class ArtigoConhecimentoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "ativo", "publico", "atualizado_em")
    list_filter = ("categoria", "ativo", "publico")
    search_fields = ("titulo", "resumo", "conteudo")
    prepopulated_fields = {"slug": ("titulo",)}


class InteracaoInline(admin.TabularInline):
    model = InteracaoChamado
    extra = 0


@admin.register(ChamadoSuporte)
class ChamadoSuporteAdmin(admin.ModelAdmin):
    list_display = ("id", "assunto", "solicitante", "categoria", "prioridade", "situacao", "atualizado_em")
    list_filter = ("situacao", "prioridade", "categoria")
    search_fields = ("assunto", "descricao", "solicitante__username")
    inlines = [InteracaoInline]
