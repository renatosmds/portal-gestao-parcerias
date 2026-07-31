from django.contrib import admin

from .models import AchadoAssistido, ProcessamentoAssistido


class AchadoInline(admin.TabularInline):
    model = AchadoAssistido
    extra = 0
    readonly_fields = ("codigo", "severidade", "titulo", "descricao", "ordem")


@admin.register(ProcessamentoAssistido)
class ProcessamentoAssistidoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "documento",
        "empresa",
        "status",
        "decisao_revisor",
        "criado_em",
    )
    list_filter = ("status", "decisao_revisor", "ia_externa_utilizada")
    search_fields = ("documento__descricao", "empresa__nome")
    inlines = [AchadoInline]
