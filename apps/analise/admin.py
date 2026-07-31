from django.contrib import admin

from .models import Analise


@admin.register(Analise)
class AnaliseAdmin(admin.ModelAdmin):
    list_display = (
        "numtermo",
        "numRA",
        "item",
        "nomeOSC",
        "empresa",
        "status",
        "concluida",
        "atualizada_em",
    )
    list_filter = (
        "empresa",
        "concluida",
        "status",
    )
    search_fields = (
        "numtermo__termo",
        "numtermo__numtermo",
        "prestacao__numtermo",
        "nomeOSC",
        "numRA",
        "item",
        "inconformidade",
        "recomendacoes",
    )
    ordering = (
        "concluida",
        "numtermo__termo",
        "numRA",
        "item",
    )
    autocomplete_fields = (
        "empresa",
        "numtermo",
        "prestacao",
    )
