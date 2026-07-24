from django.contrib import admin

from .models import Lancamento


@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_lancamento",
        "data_documento",
        "fornecedor",
        "empresa",
        "valor_documento",
        "valor_glosa",
        "situacao",
        "atestado",
    )
    list_filter = (
        "empresa",
        "situacao",
        "tipo_documento",
        "atestado",
        "data_documento",
    )
    search_fields = (
        "numero_lancamento",
        "numero_documento",
        "chave_acesso",
        "descricao",
        "fornecedor__credor",
        "fornecedor__razao",
        "fornecedor__fantasia",
        "termo__termo",
        "prestacao__numtermo",
    )
    autocomplete_fields = (
        "empresa",
        "termo",
        "prestacao",
        "fornecedor",
        "analise",
        "criado_por",
    )
    date_hierarchy = "data_documento"
