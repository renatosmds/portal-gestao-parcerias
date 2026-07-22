from rest_framework.serializers import ModelSerializer
from apps.conferencia3.models import Conferencia3


class Conferencia3Serializer(ModelSerializer):
    class Meta:
        model = Conferencia3
        fields = [
            'id', 'nome', 'ordem', 'rubricaNivel1', 'rubricaNivel2', 'rubricaNivel3', 'credor', 'tipo', 'CpfCnpj',
            'especie', 'numero', 'data', 'comprovante', 'valor', 'fileBoleto', 'fileNF', 'fileComprPag',
            'fileOrcamentos', 'photo', 'conferido', 'notificado', 'aprovado', 'notificacao'
        ]
