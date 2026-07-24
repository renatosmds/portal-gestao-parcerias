from django.contrib import admin

from .models import Termos


@admin.register(Termos)
class TermosAdmin(admin.ModelAdmin):
    list_display = (
        "termo", "numtermo", "nomeosc", "empresa", "analista",
        "inicioVigencia", "terminoVigencia", "status",
    )
    list_filter = ("empresa", "tipo", "status", "analista")
    search_fields = ("termo", "numtermo", "nomeosc", "apelido", "objeto")
    ordering = ("termo", "numtermo")
    autocomplete_fields = ("empresa",)
