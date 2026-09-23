from django.contrib import admin

from .models import Prestacao, CompetenciaPrestacao


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


@admin.register(CompetenciaPrestacao)
class CompetenciaPrestacaoAdmin(admin.ModelAdmin):
    list_display = (
        "prestacao",
        "ano",
        "mes",
        "data_inicial",
        "data_final",
        "saldo_inicial",
        "saldo_final",
        "status",
    )

    list_filter = (
        "ano",
        "mes",
        "status",
    )

    search_fields = (
        "prestacao__numtermo",
        "prestacao__credor",
    )

    ordering = (
        "-ano",
        "-mes",
    )

    fields = (
        "prestacao",
        "ano",
        "mes",
        "data_inicial",
        "data_final",
        "saldo_inicial",
        "saldo_final",
        "status",
        "observacoes",
    )

from .models import HistoricoPrestacao
admin.site.register(HistoricoPrestacao)
