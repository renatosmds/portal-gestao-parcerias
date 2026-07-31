from django.contrib import admin
from .models import AtualizacaoMeta, MetaExecucao

@admin.register(MetaExecucao)
class MetaExecucaoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "prestacao", "situacao", "valor_previsto", "valor_realizado", "atualizado_em")
    list_filter = ("situacao", "unidade")
    search_fields = ("titulo", "codigo", "prestacao__numtermo")

admin.site.register(AtualizacaoMeta)
