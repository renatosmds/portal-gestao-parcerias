from django.contrib import admin
from .models import HistoricoPublicacao, PublicacaoDocumento, PublicacaoParceria


@admin.register(PublicacaoParceria)
class PublicacaoParceriaAdmin(admin.ModelAdmin):
    list_display = ("termo", "publicada", "orgao_responsavel", "publicada_em", "publicada_por")
    list_filter = ("publicada", "orgao_responsavel")
    search_fields = ("termo__numtermo", "termo__termo", "termo__nomeosc", "termo__empresa__nome")


@admin.register(PublicacaoDocumento)
class PublicacaoDocumentoAdmin(admin.ModelAdmin):
    list_display = ("documento", "classificacao", "publicado", "publicado_em", "publicado_por")
    list_filter = ("classificacao", "publicado")
    search_fields = ("documento__descricao", "documento__numero_documento")


@admin.register(HistoricoPublicacao)
class HistoricoPublicacaoAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "acao", "termo", "documento", "usuario")
    list_filter = ("acao", "criado_em")
    readonly_fields = ("criado_em",)
