from django.contrib import admin

from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = (
        "descricao",
        "tipo",
        "empresa",
        "status",
        "percentual_conferencia",
        "conferido_por",
        "atualizado_em",
    )
    list_filter = (
        "empresa",
        "tipo",
        "status",
        "documento_legivel",
        "dados_compativeis",
        "vigencia_valida",
        "pagamento_comprovado",
        "atesto_valido",
    )
    search_fields = (
        "descricao",
        "numero_documento",
        "termo__termo",
        "termo__numtermo",
        "prestacao__numtermo",
        "lancamento__numero_lancamento",
    )
    autocomplete_fields = (
        "empresa",
        "termo",
        "prestacao",
        "lancamento",
        "conferido_por",
        "pertence",
    )
