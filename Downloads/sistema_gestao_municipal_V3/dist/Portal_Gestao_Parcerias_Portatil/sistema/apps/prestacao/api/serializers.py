from rest_framework.serializers import ModelSerializer
from apps.prestacao.models import Prestacao


class PrestacaoSerializer(ModelSerializer):
    class Meta:
        model = Prestacao
        fields = [
            'numtermo', 'cod_reduz', 'tipo_credito', 'desc_tipo_credito', 'uo', 'nome_uo', 'despesa', 'fonte',
            'programatica', 'desc_programatica', 'cod_acao', 'credito_orcamentario', 'credito_autorizado',
            'alteracoes', 'credito_provisionado', 'emp_mes', 'emp_ate_mes', 'em_liq_mes', 'em_liq_ate_mes',
            'liq_mes', 'liq_ate_mes', 'pag_mes', 'pag_ate_mes', 'saldo_credito', 'saldo_provisao',
            'saldo_empenho_aliq', 'saldo_empenho_liq', 'saldo_liquidacao'
        ]
