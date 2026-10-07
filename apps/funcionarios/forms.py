from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Funcionario, FolhaPonto, FolhaPagamento


class FuncionarioForm(forms.ModelForm):
    CAMPOS_POR_ABA = {
        "identificacao": [
            "empresa",
            "nome",
            "cargo",
            "nivel",
            "equipamento",
            "tipo_vinculo",
            "data_admissao",
            "data_desligamento",
            "de_ferias",
            "ativo",
            "curso",
        ],
        "dados_pessoais": [
            "cpf",
            "data_nascimento",
            "Telefone",
            "email",
        ],
        "endereco": [
            "endereco",
            "bairro",
            "cep",
            "cidade",
            "estado",
        ],
        "dados_funcionais": [
            "pis_pasep_nit",
            "jornada_semanal",
            "divisor_mensal",
            "termo",
            "centro_custo",
        ],
        "folha": [
            "banco",
            "agencia",
            "conta_bancaria",
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
        ],
    }

    PERMISSOES_ABAS = {
        "identificacao": {
            "view": "funcionarios.view_funcionario_identificacao",
            "change": "funcionarios.change_funcionario_identificacao",
        },
        "dados_pessoais": {
            "view": "funcionarios.view_funcionario_dados_pessoais",
            "change": "funcionarios.change_funcionario_dados_pessoais",
        },
        "endereco": {
            "view": "funcionarios.view_funcionario_endereco",
            "change": "funcionarios.change_funcionario_endereco",
        },
        "dados_funcionais": {
            "view": "funcionarios.view_funcionario_dados_funcionais",
            "change": "funcionarios.change_funcionario_dados_funcionais",
        },
        "folha": {
            "view": "funcionarios.view_funcionario_folha",
            "change": "funcionarios.change_funcionario_folha",
        },
    }

    class Meta:
        model = Funcionario
        fields = [
            "empresa",
            "nome",
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
            "cpf",
            "pis_pasep_nit",
            "data_nascimento",
            "tipo_vinculo",
            "data_admissao",
            "data_desligamento",
            "jornada_semanal",
            "divisor_mensal",
            "termo",
            "centro_custo",
            "banco",
            "agencia",
            "conta_bancaria",
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
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
        self.abas_disponiveis = {}

        # Cadastro inicial simplificado:
        # apenas Nome e CPF permanecem obrigatorios.
        campos_opcionais = [
            "usuario",
            "cargo",
            "nivel",
            "equipamento",
            "tipo_vinculo",
            "data_admissao",
            "data_desligamento",
            "de_ferias",
            "ativo",
            "curso",
            "data_nascimento",
            "Telefone",
            "email",
            "endereco",
            "bairro",
            "cep",
            "cidade",
            "estado",
            "pis_pasep_nit",
            "jornada_semanal",
            "divisor_mensal",
            "termo",
            "centro_custo",
            "banco",
            "agencia",
            "conta_bancaria",
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
        ]

        for nome_campo in campos_opcionais:
            if nome_campo in self.fields:
                self.fields[nome_campo].required = False

        if "nome" in self.fields:
            self.fields["nome"].required = True

        if "cpf" in self.fields:
            self.fields["cpf"].required = True

        if user and not user.is_superuser:
            funcionario = getattr(user, "funcionario", None)
            empresa = getattr(funcionario, "empresa", None) if funcionario else None

            if empresa and "empresa" in self.fields:
                self.fields["empresa"].queryset = (
                    self.fields["empresa"].queryset.filter(pk=empresa.pk)
                )
                self.fields["empresa"].initial = empresa

        for aba, permissoes in self.PERMISSOES_ABAS.items():
            pode_ver = (
                not user
                or user.is_superuser
                or user.has_perm(permissoes["view"])
            )

            pode_alterar = (
                not user
                or user.is_superuser
                or user.has_perm(permissoes["change"])
            )

            self.abas_disponiveis[aba] = {
                "view": pode_ver,
                "change": pode_alterar,
            }

            for nome_campo in self.CAMPOS_POR_ABA[aba]:
                if nome_campo not in self.fields:
                    continue

                if not pode_ver:
                    self.fields.pop(nome_campo, None)
                    continue

                if not pode_alterar:
                    self.fields[nome_campo].disabled = True



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

class AcessoSistemaForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Usu?rio"
        self.fields["password1"].label = "Senha inicial"
        self.fields["password2"].label = "Confirmar senha"

        self.fields["username"].help_text = (
            "Informe o nome que ser? utilizado para entrar no PGP."
        )

        self.fields["password1"].help_text = (
            "A senha deve atender aos requisitos de seguran?a do sistema."
        )

        self.fields["password2"].help_text = (
            "Digite novamente a senha para confirma??o."
        )
