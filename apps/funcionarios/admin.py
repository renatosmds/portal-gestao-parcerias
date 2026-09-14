from django.contrib import admin
from .models import Funcionario, FolhaPonto, FolhaPagamento


class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['codigo_pseudonimo', 'nome', 'usuario', 'cargo', 'nivel', 'equipamento', 'endereco', 'bairro', 'cep', 'cidade', 'estado',
                    'email', 'Telefone', 'de_ferias', 'ativo', 'salarioBase', 'salarioBruto', 'salarioLiquido',
                    'diasTrabalhados', 'avisoPrevio', 'avosFerias', 'avosTercoFerias', 'avos13Salario', 'fgts',
                    'multafgts', 'inss', 'totalVerbaRescisoria', 'totalRescisao'

                    ]

    fieldsets = (
        ('DADOS GERAIS', {
            'classes': ('collapse',),
            'fields': ('codigo_pseudonimo', ('nome', 'usuario', 'de_ferias', 'ativo'), ('cargo', 'nivel', 'equipamento'), ('Telefone', 'email'))}),

        ('DADOS DO RELATÓRIO DE AUDITORIA', {
            'classes': ('collapse',),
            'fields': (('endereco', 'bairro', 'cep'), ('cidade', 'estado'),  'user', 'curso', 'departamentos',
                       'empresa'
                       )}),
    )

    readonly_fields = ('codigo_pseudonimo',)

    list_filter = ('nome', 'usuario', 'cargo', 'nivel', 'equipamento', 'endereco', 'bairro', 'cep', 'cidade',
                   'estado', 'email', 'Telefone', 'de_ferias', 'ativo', 'salarioBase', 'salarioBruto', 'salarioLiquido',
                   'diasTrabalhados', 'avisoPrevio', 'avosFerias', 'avosTercoFerias', 'avos13Salario', 'fgts',
                   'multafgts', 'inss', 'totalVerbaRescisoria', 'totalRescisao', 'curso')

    search_fields = ('codigo_pseudonimo', 'nome', 'usuario', 'cargo', 'nivel', 'equipamento', 'endereco', 'bairro', 'cep', 'cidade',
                   'estado', 'email', 'Telefone', 'de_ferias', 'ativo', 'salarioBase', 'salarioBruto', 'salarioLiquido',
                   'diasTrabalhados', 'avisoPrevio', 'avosFerias', 'avosTercoFerias', 'avos13Salario', 'fgts',
                   'multafgts', 'inss', 'totalVerbaRescisoria', 'totalRescisao', 'curso')


admin.site.register(Funcionario, FuncionarioAdmin)

admin.site.register(FolhaPonto)
admin.site.register(FolhaPagamento)
