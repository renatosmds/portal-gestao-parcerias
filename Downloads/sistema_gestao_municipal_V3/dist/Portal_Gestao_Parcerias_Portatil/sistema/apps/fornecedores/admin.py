from django.contrib import admin

from .models import Fornecedores


@admin.register(Fornecedores)
class FornecedoresAdmin(admin.ModelAdmin):
    list_display = (
        "credor",
        "pessoa",
        "tipo",
        "numero",
        "empresa",
        "cidade",
        "estado",
        "telefone",
    )
    list_filter = (
        "empresa",
        "pessoa",
        "tipo",
        "estado",
    )
    search_fields = (
        "credor",
        "razao",
        "fantasia",
        "numero",
        "email",
        "telefone",
    )
    ordering = ("credor",)
    autocomplete_fields = ("empresa",)
