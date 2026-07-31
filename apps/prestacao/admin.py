from django.contrib import admin

from .models import Prestacao


@admin.register(Prestacao)
class PrestacaoAdmin(admin.ModelAdmin):
    list_display = (
        "numtermo",
        "tipoTermo",
        "credor",
        "empresa",
        "valorContrato",
        "qtdParcelas",
        "concluida",
    )
    list_filter = (
        "empresa",
        "tipoTermo",
        "tipo",
        "concluida",
    )
    search_fields = (
        "numtermo",
        "credor",
        "CpfCnpj",
        "gestora",
        "matricula",
    )
    ordering = (
        "concluida",
        "numtermo",
        "credor",
    )
    autocomplete_fields = ("empresa",)

from .models import HistoricoPrestacao
admin.site.register(HistoricoPrestacao)
