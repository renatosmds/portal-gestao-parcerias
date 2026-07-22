from rest_framework.serializers import ModelSerializer
from apps.clientes.models import Clientes


class ClientesSerializer(ModelSerializer):
    class Meta:
        model = Clientes
        fields = [
            'first_name', 'last_name', 'age', 'salary', 'bio', 'photo'
        ]
