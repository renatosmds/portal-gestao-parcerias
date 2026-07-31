from django.contrib import admin

from .models import Parcerias


@admin.register(Parcerias)
class ParceriasAdmin(admin.ModelAdmin):
    list_display = (
        "numtermo",
        "nomeOSC",
        "empresa",
        "credor",
        "concluido",
        "prazoFinal",
    )
    list_filter = (
        "empresa",
        "concluido",
    )
    search_fields = (
        "nomeOSC",
        "numtermo__termo",
        "numtermo__numtermo",
        "credor__credor",
        "status",
    )
    ordering = (
        "concluido",
        "numtermo__termo",
        "nomeOSC",
    )
    autocomplete_fields = (
        "empresa",
        "numtermo",
        "credor",
    )
