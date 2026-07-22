from django.contrib import admin
# from import_export import resources
# from import_export.admin import ImportExportModelAdmin
from .models import Termos


class TermosAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'termo', 'apelido', 'relatoriosDeSinteses',
                  'inicioVigencia', 'terminoVigencia','analista', 'status','saldoDashboard',
                  'saldoContaSinteseDespesas', 'rendimento', 'saldoContaSinteseMovFinanceira','valorDevolvido',
                  'saldoFinal','totalDeLacamentos', 'lacamentosRegulares', 'lacamentosIrregulares',
                  'lacamentosGlosados', 'lacamentosNaoEnviados', 'naoanalisados', 'total','extratosBancarios',
                  'pendenciasOfx','valoresGlosados', 'glosasRestituidas', 'saldoGlosas']

    fieldsets = (
        ('Dados Gerais', {'fields': (
            ('numtermo', 'nomeosc'), ('numdispensa', 'numpa'), ('valorglobal', 'valorrepasse', 'valorsaldo'),
         ('parcelasAbertas', 'assinatura', 'nomemunicipio'))}),
        ('Dados Complementares', {
            'classes': ('collapse',),
            'fields': [('nomeintermediario', 'nomesecretario', 'nomerepresentante'), ('tipo', 'termo', 'apelido',), ('parceria', 'objeto',), ('relatoriosDeSinteses',
                  'inicioVigencia', 'terminoVigencia',), ('analista', 'status',), ('saldoDashboard',
                  'saldoContaSinteseDespesas', 'rendimento',), ('saldoContaSinteseMovFinanceira','valorDevolvido',
                  'saldoFinal',), ('totalDeLacamentos', 'lacamentosRegulares', 'lacamentosIrregulares',),
                       ('lacamentosGlosados','lacamentosNaoEnviados', 'naoanalisados',), ('total','extratosBancarios',
                  'pendenciasOfx',), ('valoresGlosados', 'glosasRestituidas', 'saldoGlosas',), 'observacoes']
        })


    )
    list_filter = ('numtermo', 'nomeosc', 'numdispensa', 'numpa', 'valorglobal', 'valorrepasse', 'valorsaldo',
                   'parcelasAbertas', 'tipo', 'termo', 'apelido', 'parceria', 'objeto', 'relatoriosDeSinteses',
                  'inicioVigencia', 'terminoVigencia', 'analista', 'status', 'saldoDashboard',
                  'saldoContaSinteseDespesas', 'rendimento', 'saldoContaSinteseMovFinanceira', 'valorDevolvido',
                  'saldoFinal', 'totalDeLacamentos', 'lacamentosRegulares', 'lacamentosIrregulares',
                  'lacamentosGlosados', 'lacamentosNaoEnviados', 'naoanalisados', 'total', 'extratosBancarios',
                  'pendenciasOfx', 'valoresGlosados', 'glosasRestituidas', 'saldoGlosas', 'observacoes')

    search_fields = ('numtermo', 'nomeosc', 'numdispensa', 'numpa', 'valorglobal', 'valorrepasse', 'valorsaldo',
                     'parcelasAbertas', 'tipo', 'termo', 'apelido', 'parceria', 'objeto', 'relatoriosDeSinteses',
                  'inicioVigencia', 'terminoVigencia', 'analista', 'status', 'saldoDashboard',
                  'saldoContaSinteseDespesas', 'rendimento', 'saldoContaSinteseMovFinanceira', 'valorDevolvido',
                  'saldoFinal', 'totalDeLacamentos', 'lacamentosRegulares', 'lacamentosIrregulares',
                  'lacamentosGlosados', 'lacamentosNaoEnviados', 'naoanalisados', 'total', 'extratosBancarios',
                  'pendenciasOfx', 'valoresGlosados', 'glosasRestituidas', 'saldoGlosas', 'observacoes')






admin.site.register(Termos, TermosAdmin)


# class ClienteResource(resources.ModelResource):
#     class Meta:
#         model = Termos
#
# @admin.registe(Termos)
# class ClienteAdmin(ImportExportModelAdmin):
#     resource_class = ClienteResource