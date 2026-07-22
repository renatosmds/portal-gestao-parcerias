from django.contrib import admin
from .models import Fornecedores


class FornecedoresAdmin(admin.ModelAdmin):
    list_display = ['credor', 'pessoa', 'razao', 'tipo', 'numero', 'fantasia', 'endereco', 'bairro', 'cep', 'cidade',
                    'estado', 'email', 'telefone', 'iestadual', 'imunicipal']

    fieldsets = (
        ('DADOS GERAIS', {
            'classes': ('collapse',),
            'fields': ('credor', 'tipo', 'numero')}),

        ('DADOS DO RELATÓRIO DE AUDITORIA', {
            'classes': ('collapse',),
            'fields': (('pessoa', 'razao', 'fantasia'), ('iestadual', 'imunicipal'), ('endereco', 'bairro', 'cep'),
                       ('cidade', 'estado'), ('email', 'telefone')
                       )}),
    )

    list_filter = ('credor', 'pessoa', 'razao', 'tipo', 'numero', 'fantasia', 'endereco', 'bairro', 'cep', 'cidade',
                   'estado', 'email', 'telefone', 'iestadual', 'imunicipal')

    search_fields = ('credor', 'pessoa', 'razao', 'tipo', 'numero', 'fantasia', 'endereco', 'bairro', 'cep', 'cidade',
                     'estado', 'email', 'telefone', 'iestadual', 'imunicipal')


admin.site.register(Fornecedores, FornecedoresAdmin)
