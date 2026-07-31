from django.forms import ModelForm
from .models import Receitas


class ReceitasForm(ModelForm):
    class Meta:
        model = Receitas
        fields = ['numtermo', 'osc', 'parcela', 'ente', 'fonte', 'conta', 'data', 'saldoAnterior', 'repasse', 'depositoOsc',
                  'rendimento', 'creditoAutorizado', 'resgateAutomatico', 'estorno', 'totalReceitas', 'aplicacao',
                  'debitoAutorizado', 'despesaBancaria', 'impostoRenda', 'iof', 'despesas', 'totalDespesas',
                  'saldoBancario', 'fileNap', 'fileDepositoTicket', 'fileDepositoOsc', 'fileAplicacao',
                  'fileContrapartida', 'fileEstorno', 'conferido', 'notificado', 'aprovado', 'notificacao'
                  ]
