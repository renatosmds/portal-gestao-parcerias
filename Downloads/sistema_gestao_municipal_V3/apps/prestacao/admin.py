from django.contrib import admin
from .models import Prestacao


class PrestacaoAdmin(admin.ModelAdmin):
    list_display = ['tipoTermo', 'numtermo', 'termoAditivo', 'credor', 'CpfCnpj',
                    'fonte', 'bancoCredor', 'agCredor', 'ccCredor', 'cod_reduz', 'gestora', 'contato',
                    'valorContrato', 'qtdParcelas', 'concluida'
                    ]

    fieldsets = (
        ('Dados Gerais',
         {'fields': (('tipoTermo', 'numtermo', 'termoAditivo'), ('credor', 'numCredor'), ('tipo', 'CpfCnpj'),
                     ('oficioCcoaf', 'sco'), ('agCredito', 'ccCredito'), ('uo', 'funcao', 'subfuncao'),
                     ('programa', 'projeto', 'natureza'), ('fonte', 'gestora'), ('bancoCredor', 'agCredor', 'ccCredor'),
                     ('cod_reduz', 'matricula', 'contato'), ('valorContrato', 'qtdParcelas', 'concluida'))}),
        ('Dados Complementares', {
            'classes': ('collapse',),
            'fields': [('mesParcela1', 'anoParcela1', 'valorParcela1', 'empenhoParcela1', 'napParcela1',
                        'dataNapParcela1'), ('mesParcela2', 'anoParcela2', 'valorParcela2', 'empenhoParcela2',
                                             'napParcela2', 'dataNapParcela2'), ('mesParcela3', 'anoParcela3',
                                                                                 'valorParcela3', 'empenhoParcela3',
                                                                                 'napParcela3', 'dataNapParcela3'),
                       ('mesParcela4', 'anoParcela4', 'valorParcela4', 'empenhoParcela4', 'napParcela4',
                        'dataNapParcela4'), ('mesParcela5', 'anoParcela5', 'valorParcela5', 'empenhoParcela5',
                                             'napParcela5', 'dataNapParcela5'), ('mesParcela6', 'anoParcela6',
                                                                                 'valorParcela6', 'empenhoParcela6',
                                                                                 'napParcela6', 'dataNapParcela6'),
                       ('mesParcela7', 'anoParcela7', 'valorParcela7', 'empenhoParcela7', 'napParcela7',
                        'dataNapParcela7'), ('mesParcela8', 'anoParcela8', 'valorParcela8', 'empenhoParcela8',
                                             'napParcela8', 'dataNapParcela8'), ('mesParcela9', 'anoParcela9',
                                                                                 'valorParcela9', 'empenhoParcela9',
                                                                                 'napParcela9', 'dataNapParcela9'),
                       ('mesParcela10', 'anoParcela10', 'valorParcela10', 'empenhoParcela10', 'napParcela10',
                        'dataNapParcela10'), ('mesParcela11', 'anoParcela11', 'valorParcela11', 'empenhoParcela11',
                                              'napParcela11', 'dataNapParcela11'), ('mesParcela12', 'anoParcela12',
                                                                                    'valorParcela12',
                                                                                    'empenhoParcela12', 'napParcela12',
                                                                                    'dataNapParcela12')
                       ]
        })
    )

    list_filter = ('tipoTermo', 'numtermo', 'termoAditivo', 'credor', 'CpfCnpj', 'fonte', 'bancoCredor', 'agCredor',
                   'ccCredor', 'cod_reduz', 'gestora', 'concluida',)

    search_fields = ('tipoTermo', 'numtermo', 'termoAditivo', 'credor', 'CpfCnpj', 'fonte', 'bancoCredor', 'agCredor',
                     'ccCredor', 'cod_reduz', 'gestora', 'concluida')


admin.site.register(Prestacao, PrestacaoAdmin)
