from rest_framework.serializers import ModelSerializer

from apps.analise.models import Analise


class AnaliseSerializer(ModelSerializer):
    class Meta:
        model = Analise
        fields = [
            "id",
            "empresa",
            "numtermo",
            "prestacao",
            "nomeOSC",
            "numRA",
            "item",
            "inconformidade",
            "recomendacoes",
            "posicaoSecretaria",
            "status",
            "concluida",
            "criada_em",
            "atualizada_em",
        ]
        read_only_fields = [
            "empresa",
            "criada_em",
            "atualizada_em",
        ]
