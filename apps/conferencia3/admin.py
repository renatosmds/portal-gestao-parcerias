from django.contrib import admin
from .models import Conferencia3


class Conferencia3Admin(admin.ModelAdmin):
    list_display = ['numtermo', 'parcela', 'ordem', 'credor', 'tipo', 'CpfCnpj', 'especie', 'numero', 'data',
                    'comprovante', 'valor', 'conferido', 'notificado', 'aprovado'
                    ]

    fieldsets = (
        ('Dados Gerais', {'fields': (('numtermo', 'parcela'), ('ordem', 'credor', 'valor'))}),
        ('Dados Complementares', {
            'classes': ('collapse',),
            'fields': [('rubricaNivel1'), ('rubricaNivel2'), ('rubricaNivel3'), ('tipo', 'CpfCnpj'),
                       ('especie', 'numero'), ('data', 'comprovante'), ('conferido', 'notificado',
                        'aprovado'), ('notificacao'), ('fileBoleto'), ('fileNF'), ('fileComprPag'), ('fileOrcamentos')
                       ]
        }
         )
    )

    list_filter = ('numtermo', 'parcela', 'ordem', 'credor', 'tipo', 'CpfCnpj', 'especie', 'numero', 'data',
                   'comprovante', 'valor', 'conferido', 'notificado', 'aprovado',)

    search_fields = ('numtermo', 'parcela', 'ordem', 'credor', 'tipo', 'CpfCnpj', 'especie', 'numero', 'data',
                     'comprovante', 'valor', 'conferido', 'notificado', 'aprovado')


admin.site.register(Conferencia3, Conferencia3Admin)
