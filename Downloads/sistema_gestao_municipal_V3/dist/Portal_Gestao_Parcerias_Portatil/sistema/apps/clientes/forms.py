from django.forms import ModelForm
from .models import Clientes


class ClientesForm(ModelForm):
    class Meta:
        model = Clientes
        fields = ['first_name', 'last_name', 'age', 'salary', 'bio', 'photo']
