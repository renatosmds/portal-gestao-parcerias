from django.contrib import admin
from .models import Importacao

@admin.register(Importacao)
class ImportacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "tipo", "arquivo_nome", "situacao", "total_lido", "total_erros", "criado_em")
    list_filter = ("tipo", "situacao", "sistema_origem")
    search_fields = ("arquivo_nome", "sistema_origem")
    readonly_fields = ("cabecalhos", "linhas", "erros", "criado_em", "confirmado_em")
