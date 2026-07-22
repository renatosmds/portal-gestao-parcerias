from django.contrib import admin
from .models import Parcerias


class ParceriasAdmin(admin.ModelAdmin):
    list_display = ['numtermo', 'nomeOSC', 'fileTC', 'numRA', 'numOficioRA', 'fileRA', 'fileOficioRA', 'dtRaSMDS',
                    'respRA', 'numRE', 'numOficioRE', 'fileRE', 'fileOficioRE', 'dtReSMDS', 'respRE', 'fileRRE',
                    'prazoFinal', 'status', 'prazoDecorrido', 'prazoRestante', 'historico', 'concluido', 'photo']

    fieldsets = (
        ('DADOS GERAIS', {
            'classes': ('collapse',),
            'fields': (('numtermo', 'nomeOSC', 'fileTC'), ('prazoFinal', 'prazoDecorrido', 'prazoRestante', 'status',
                                                           'historico', 'concluido', 'photo'))}),

        ('DADOS DO RELATÓRIO DE AUDITORIA', {
            'classes': ('collapse',),
            'fields': (('numRA', 'fileRA'), ('numOficioRA', 'fileOficioRA'), ('dtRaSMDS', 'respRA'),)}),

        ('DADOS DO RELATÓRIO DE EFETIVIDADE', {
            'classes': ('collapse',),
            'fields': ((('numRE',  'fileRE'), ('numOficioRE', 'fileOficioRE'), ('dtReSMDS', 'respRE', 'fileRRE'),
                        ))}),

    )


admin.site.register(Parcerias, ParceriasAdmin)
