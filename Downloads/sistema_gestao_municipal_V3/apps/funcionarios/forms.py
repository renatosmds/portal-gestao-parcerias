from django import forms

from .models import Funcionario, FolhaPonto, FolhaPagamento


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
            "cpf", "pis_pasep_nit", "data_nascimento", "tipo_vinculo",
            "data_admissao", "data_desligamento", "jornada_semanal", "divisor_mensal",
            "termo", "centro_custo", "banco", "agencia", "conta_bancaria",
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


class DateInput(forms.DateInput):
    input_type = "date"


class FolhaPontoForm(forms.ModelForm):
    class Meta:
        model = FolhaPonto
        fields = ["funcionario", "competencia", "horas_previstas", "horas_trabalhadas", "horas_extras", "horas_faltas_atrasos", "banco_horas", "observacoes"]
        widgets = {"competencia": DateInput()}


class FolhaPagamentoForm(forms.ModelForm):
    class Meta:
        model = FolhaPagamento
        fields = ["funcionario", "folha_ponto", "competencia", "salario_base", "adicional_percentual_hora_extra", "outras_verbas", "inss", "irrf", "vale_transporte", "pensao", "outros_descontos", "observacoes"]
        widgets = {"competencia": DateInput()}

    def clean(self):
        cleaned = super().clean()
        funcionario = cleaned.get("funcionario")
        ponto = cleaned.get("folha_ponto")
        if ponto and funcionario and ponto.funcionario_id != funcionario.id:
            self.add_error("folha_ponto", "A folha de ponto deve pertencer ao mesmo funcionário.")
        return cleaned
