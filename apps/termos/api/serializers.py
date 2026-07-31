from rest_framework import serializers
from apps.termos.models import Termos
from apps.registro_hora_extra.api.serializers import RegistroHoraExtraSerializer


class TermosSerializer(serializers.ModelSerializer):
    registrohoraextra_set = RegistroHoraExtraSerializer(many=True)

    class Meta:
        model = Termos
        fields = (
            'nomeOSC', 'numTermo', 'numPa', 'vigencia', 'assinatura', 'valorGlobal', 'valorRepasse', 'valorSaldo',
            'numDispensa', 'nomeMunicipio', 'nomeIntermediario', 'nomeSecretario', 'nomeRepresentante', 'fileOficio'
            , 'fileTermo', 'filePlanoTrabalho', 'fileEmpenho', 'fileNap', 'fileAtesto', 'fileCertidao', 'fileOficioFia')
