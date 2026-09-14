from django.contrib import admin

from .models import Fornecedores


@admin.register(Fornecedores)
class FornecedoresAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_pseudonimo",
        "credor",
        "pessoa",
        "tipo",
        "numero",
        "empresa",
        "cidade",
        "estado",
        "telefone",
    )
    readonly_fields = ("codigo_pseudonimo",)

    list_filter = (
        "empresa",
        "pessoa",
        "tipo",
        "estado",
    )
    search_fields = (
        "codigo_pseudonimo",
        "credor",
        "razao",
        "fantasia",
        "numero",
        "email",
        "telefone",
    )
    ordering = ("credor",)
    autocomplete_fields = ("empresa",)
