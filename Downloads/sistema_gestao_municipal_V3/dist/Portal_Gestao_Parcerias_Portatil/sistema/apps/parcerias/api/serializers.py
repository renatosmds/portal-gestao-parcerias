from rest_framework.serializers import ModelSerializer
from apps.parcerias.models import Parcerias


class ParceriasSerializer(ModelSerializer):
    class Meta:
        model = Parcerias
        fields = ['numtermo', 'nomeOSC', 'fileTC', 'numRA', 'numOficioRA', 'fileRA', 'fileOficioRA', 'dtRaSMDS',
                  'respRA', 'numRE', 'numOficioRE', 'fileRE', 'fileOficioRE', 'dtReSMDS', 'respRE', 'fileRRE',
                  'prazoFinal', 'status', 'prazoDecorrido', 'prazoRestante', 'historico', 'photo'
                  ]
