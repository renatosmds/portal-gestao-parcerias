from django import forms

from .models import Funcionario


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            "nome",
            "usuario",
            "cargo",
            "nivel",
            "equipamento",
            "endereco",
            "bairro",
            "cep",
            "cidade",
            "estado",
            "email",
            "Telefone",
            "de_ferias",
            "ativo",
            "salarioBase",
            "salarioBruto",
            "salarioLiquido",
            "diasTrabalhados",
            "avisoPrevio",
            "avosFerias",
            "avosTercoFerias",
            "avos13Salario",
            "fgts",
            "multafgts",
            "inss",
            "totalVerbaRescisoria",
            "totalRescisao",
            "curso",
            "conferencia3",
        ]

    def clean_usuario(self):
        usuario = (self.cleaned_data.get("usuario") or "").strip()
        if not usuario:
            raise forms.ValidationError("Informe o nome de usuário.")
        return usuario
