# coding=utf-8
from django.contrib import admin
from .models import Receitas


class ReceitasAdmin(admin.ModelAdmin):
    list_display = ('data', 'saldoAnterior', 'repasse', 'depositoOsc',
                    'rendimento', 'creditoAutorizado', 'resgateAutomatico', 'estorno', 'totalReceitas', 'aplicacao',
                    'debitoAutorizado', 'despesaBancaria', 'impostoRenda', 'iof', 'despesas', 'totalDespesas',
                    'saldoBancario', 'conferido', 'notificado', 'aprovado', 'notificacao')

    fieldsets = (
        ('DADOS DA PARCERIA', {
            'classes': ('collapse',),
            'fields': (
                'osc', 'numtermo', ('parcela', 'ente', 'fonte', 'conta'), ('saldoAnterior', 'totalReceitas', 'totalDespesas',
                                                               'saldoBancario',))}),

        ('CONCILIAÇÃO BANCÁRIA - RECEITAS', {
            'classes': ('collapse',),
            'fields': ('data', ('repasse', 'depositoOsc', 'rendimento'), ('creditoAutorizado',
                                                                          'resgateAutomatico', 'estorno',))}),

        ('CONCILIAÇÃO BANCÁRIA - DESPESAS', {
            'classes': ('collapse',),
            'fields': (('aplicacao', 'debitoAutorizado', 'despesaBancaria'), ('impostoRenda', 'iof', 'despesas'))}),

        ('DOWNLOAD  - ARQUIVOS', {
            'classes': ('collapse',),
            'fields': (('fileNap', 'fileDepositoTicket', 'fileDepositoOsc', 'fileAplicacao', 'fileContrapartida',
                        'fileEstorno', 'conferido', 'notificado', 'aprovado', 'notificacao'))}),
    )


list_filter = ('numtermo', 'osc', 'parcela', 'ente', 'fonte', 'conta', 'data', 'saldoAnterior', 'repasse', 'depositoOsc',
               'rendimento', 'creditoAutorizado', 'resgateAutomatico', 'estorno', 'totalReceitas', 'aplicacao',
               'debitoAutorizado', 'despesaBancaria', 'impostoRenda', 'iof', 'despesas', 'totalDespesas',
               'saldoBancario', 'fileNap', 'fileDepositoTicket', 'fileDepositoOsc', 'fileAplicacao',
               'fileContrapartida', 'fileEstorno', 'conferido', 'notificado', 'aprovado', 'notificacao')

search_fields = ('numtermo', 'osc', 'parcela', 'ente', 'fonte', 'conta', 'data', 'saldoAnterior', 'repasse', 'depositoOsc',
                 'rendimento', 'creditoAutorizado', 'resgateAutomatico', 'estorno', 'totalReceitas', 'aplicacao',
                 'debitoAutorizado', 'despesaBancaria', 'impostoRenda', 'iof', 'despesas', 'totalDespesas',
                 'saldoBancario', 'fileNap', 'fileDepositoTicket', 'fileDepositoOsc', 'fileAplicacao',
                 'fileContrapartida', 'fileEstorno', 'conferido', 'notificado', 'aprovado', 'notificacao')

admin.site.register(Receitas, ReceitasAdmin)
