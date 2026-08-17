from django.contrib import admin

from .models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)


class ItemPlanoTrabalhoInline(admin.TabularInline):
    model = ItemPlanoTrabalho
    extra = 0


@admin.register(PlanoTrabalho)
class PlanoTrabalhoAdmin(admin.ModelAdmin):

    list_display = (
        "termo",
        "versao",
        "versao_anterior",
        "origem",
        "situacao",
        "data_eficacia",
        "inicio_vigencia",
        "fim_vigencia",
    )

    list_filter = (
        "situacao",
        "origem",
    )

    search_fields = (
        "termo__numtermo",
        "termo__termo",
        "titulo",
    )

    inlines = [
        ItemPlanoTrabalhoInline
    ]


@admin.register(ItemPlanoTrabalho)
class ItemPlanoTrabalhoAdmin(admin.ModelAdmin):

    list_display = (
        "codigo",
        "plano",
        "rubrica_nivel_1",
        "rubrica_nivel_2",
        "rubrica_nivel_3",
        "valor_total_previsto",
        "ativo",
    )

    list_filter = (
        "ativo",
        "plano__situacao",
    )

    search_fields = (
        "codigo",
        "descricao",
        "rubrica_nivel_1",
        "rubrica_nivel_2",
        "rubrica_nivel_3",
    )

