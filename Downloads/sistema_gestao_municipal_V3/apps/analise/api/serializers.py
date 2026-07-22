from rest_framework.serializers import ModelSerializer
from apps.analise.models import Analise


class AnaliseSerializer(ModelSerializer):
    class Meta:
        model = Analise
        fields = [
            'numtermo', 'nomeOSC', 'numRA', 'item', 'inconformidade', 'recomendacoes', 'posicaoSecretaria', 'status'
        ]
