from django.forms import ModelForm

from apps.funcionarios.models import Funcionario
from .models import RegistroHoraExtra


class RegistroHoraExtraForm(ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Funcionario.objects.filter(ativo=True).order_by("nome")
        if user and not user.is_superuser:
            funcionario = getattr(user, "funcionario", None)
            empresa = getattr(funcionario, "empresa", None) if funcionario else None
            queryset = queryset.filter(empresa=empresa) if empresa else queryset.none()
        self.fields["funcionario"].queryset = queryset

    class Meta:
        model = RegistroHoraExtra
        fields = ["motivo", "assunto", "funcionario", "horas"]
