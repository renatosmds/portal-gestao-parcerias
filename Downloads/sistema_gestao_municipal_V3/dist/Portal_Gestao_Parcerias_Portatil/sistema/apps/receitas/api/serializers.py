from rest_framework.serializers import ModelSerializer
from apps.receitas.models import Receitas


class ReceitasSerializer(ModelSerializer):
    class Meta:
        model = Receitas
        fields = [
            'id', 'osc', 'parcela', 'ente', 'fonte', 'conta', 'data', 'saldoAnterior', 'repasse', 'depositoOsc',
            'rendimento', 'creditoAutorizado', 'resgateAutomatico', 'estorno', 'totalReceitas', 'aplicacao',
            'debitoAutorizado', 'despesaBancaria', 'impostoRenda', 'iof', 'despesas', 'totalDespesas',
            'saldoBancario', 'fileNap', 'fileDepositoTicket', 'fileDepositoOsc', 'fileAplicacao',
            'fileContrapartida', 'fileEstorno', 'conferido', 'notificado', 'aprovado', 'notificacao'
        ]
