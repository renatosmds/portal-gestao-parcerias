from django import forms

from apps.departamentos.models import Departamento

from apps.empresas.models import Empresa
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Cargo, Equipamento, Funcionario, Nivel, FolhaPonto, FolhaPagamento, EscalaFuncionario, EscalaTrabalho, JornadaEscala


class FuncionarioForm(forms.ModelForm):
    CAMPOS_POR_ABA = {
        "identificacao": [
            "empresa",
            "nome",
            "cargo",
            "nivel",
            "equipamento",
            "departamentos",
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
            "departamentos",
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
        # Lotacao organizacional restrita a empresa do colaborador.
        queryset_lotacao_empresa = None

        if getattr(self.instance, "empresa_id", None):
            queryset_lotacao_empresa = self.instance.empresa
        elif user and not user.is_superuser:
            funcionario_usuario = getattr(
                user,
                "funcionario",
                None,
            )
            queryset_lotacao_empresa = getattr(
                funcionario_usuario,
                "empresa",
                None,
            )

        if queryset_lotacao_empresa:
            if "cargo" in self.fields:
                self.fields["cargo"].queryset = (
                    Cargo.objects.filter(
                        empresa=queryset_lotacao_empresa,
                    ).order_by("nome")
                )

            if "nivel" in self.fields:
                self.fields["nivel"].queryset = (
                    Nivel.objects.filter(
                        empresa=queryset_lotacao_empresa,
                    ).order_by("ordem", "nome")
                )

            if "equipamento" in self.fields:
                self.fields["equipamento"].queryset = (
                    Equipamento.objects.filter(
                        empresa=queryset_lotacao_empresa,
                    ).order_by("nome")
                )

            if "departamentos" in self.fields:
                self.fields["departamentos"].queryset = (
                    Departamento.objects.filter(
                        empresa=queryset_lotacao_empresa,
                    ).order_by("nome")
                )

        if "departamentos" in self.fields:
            self.fields["departamentos"].label = (
                "Unidade(s) organizacional(is)"
            )

        campos_opcionais = [
            "usuario",
            "cargo",
            "nivel",
            "equipamento",
            "departamentos",
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



    def clean(self):
        cleaned_data = super().clean()

        empresa = cleaned_data.get("empresa")

        if not empresa:
            return cleaned_data

        for campo in (
            "cargo",
            "nivel",
            "equipamento",
        ):
            objeto = cleaned_data.get(campo)

            if (
                objeto
                and objeto.empresa_id != empresa.pk
            ):
                self.add_error(
                    campo,
                    (
                        "O cadastro selecionado pertence "
                        "a outra empresa."
                    ),
                )

        departamentos = cleaned_data.get(
            "departamentos"
        )

        if empresa and departamentos is not None:
            if departamentos.exclude(
                empresa=empresa
            ).exists():
                self.add_error(
                    "departamentos",
                    (
                        "Lotacao selecionada pertence a outra empresa."
                    ),
                )

        return cleaned_data


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "format",
            "%Y-%m-%d",
        )

        super().__init__(
            *args,
            **kwargs,
        )


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



# ============================================================
# INTERFACE TRABALHISTA INTEGRADA
# ============================================================

from django.forms import inlineformset_factory

from .models import DiaFolhaPonto


class FolhaPontoOperacionalForm(forms.ModelForm):
    """
    Na interface operacional, os totais mensais nao sao
    digitados. Eles sao derivados do calendario diario.
    """

    class Meta:
        model = FolhaPonto
        fields = [
            "funcionario",
            "competencia",
            "observacoes",
        ]
        widgets = {
            "competencia": DateInput(format="%Y-%m-%d"),
            "observacoes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-control",
                }
            ),
        }


class DiaFolhaPontoForm(forms.ModelForm):

    class Meta:
        model = DiaFolhaPonto
        fields = [
            "entrada_1",
            "saida_1",
            "entrada_2",
            "saida_2",
        ]

        widgets = {
            "entrada_1": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "step": "60",
                    "class": "form-control form-control-sm",
                },
            ),
            "saida_1": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "step": "60",
                    "class": "form-control form-control-sm",
                },
            ),
            "entrada_2": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "step": "60",
                    "class": "form-control form-control-sm",
                },
            ),
            "saida_2": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "step": "60",
                    "class": "form-control form-control-sm",
                },
            ),
        }


DiaFolhaPontoFormSet = inlineformset_factory(
    FolhaPonto,
    DiaFolhaPonto,
    form=DiaFolhaPontoForm,
    extra=0,
    can_delete=False,
)




# ============================================================
# ESCALAS / JORNADAS / VINCULOS
# ============================================================


class EscalaTrabalhoForm(forms.ModelForm):

    class Meta:
        model = EscalaTrabalho

        fields = [
            "empresa",
            "nome",
            "tipo",
            "ciclo_dias",
            "jornada_semanal_referencia",
            "data_inicio",
            "data_fim",
            "fundamento",
            "ativo",
            "observacoes",
        ]

        widgets = {
            "data_inicio": DateInput(),
            "data_fim": DateInput(),
            "fundamento": forms.Textarea(
                attrs={
                    "rows": 2,
                }
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "rows": 2,
                }
            ),
        }


class JornadaEscalaForm(forms.ModelForm):

    class Meta:
        model = JornadaEscala

        fields = [
            "posicao_ciclo",
            "trabalha",
            "horas_previstas",
            "hora_entrada",
            "hora_saida",
            "intervalo_minutos",
            "descricao",
        ]

        widgets = {
            "hora_entrada": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "step": "60",
                },
            ),
            "hora_saida": forms.TimeInput(
                format="%H:%M",
                attrs={
                    "type": "time",
                    "step": "60",
                },
            ),
        }


JornadaEscalaFormSet = inlineformset_factory(
    EscalaTrabalho,
    JornadaEscala,
    form=JornadaEscalaForm,
    extra=0,
    can_delete=True,
)


JornadaEscalaNovoFormSet = inlineformset_factory(
    EscalaTrabalho,
    JornadaEscala,
    form=JornadaEscalaForm,
    extra=7,
    can_delete=True,
)


class EscalaFuncionarioForm(forms.ModelForm):

    class Meta:
        model = EscalaFuncionario

        fields = [
            "funcionario",
            "escala",
            "data_inicio",
            "data_fim",
            "data_referencia",
            "observacoes",
        ]

        widgets = {
            "data_inicio": DateInput(),
            "data_fim": DateInput(),
            "data_referencia": DateInput(),
            "observacoes": forms.Textarea(
                attrs={
                    "rows": 2,
                }
            ),
        }

    def clean(self):

        cleaned = super().clean()

        funcionario = cleaned.get(
            "funcionario"
        )

        escala = cleaned.get(
            "escala"
        )

        if (
            funcionario
            and escala
            and funcionario.empresa_id
            != escala.empresa_id
        ):

            self.add_error(
                "escala",
                (
                    "A escala deve pertencer "
                    "a mesma empresa do colaborador."
                ),
            )

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

        self.fields["username"].label = "Usuário"
        self.fields["password1"].label = "Senha inicial"
        self.fields["password2"].label = "Confirmar senha"

        self.fields["username"].help_text = (
            "Informe o nome que será utilizado para entrar no PGP."
        )

        self.fields["password1"].help_text = (
            "A senha deve atender aos requisitos de segurança do sistema."
        )

        self.fields["password2"].help_text = (
            "Digite novamente a senha para confirmação."
        )



class CadastroFuncionarioBaseForm(forms.ModelForm):
    def __init__(
        self,
        *args,
        empresa=None,
        permitir_empresa=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.empresa = empresa

        if permitir_empresa:
            self.fields["empresa"] = forms.ModelChoiceField(
                queryset=Empresa.objects.order_by("nome"),
                required=True,
                label="Empresa",
            )
            if self.instance.pk:
                self.fields["empresa"].initial = (
                    self.instance.empresa
                )

        for campo in self.fields.values():
            classes = campo.widget.attrs.get("class", "")
            campo.widget.attrs["class"] = (
                classes + " form-control"
            ).strip()

        if "empresa" in self.fields:
            self.fields["empresa"].widget.attrs["class"] = (
                "form-control"
            )

        if "ativo" in self.fields:
            self.fields["ativo"].widget.attrs["class"] = (
                "form-check-input"
            )

    def clean_nome(self):
        nome = (self.cleaned_data.get("nome") or "").strip()

        if not nome:
            raise forms.ValidationError(
                "Informe o nome."
            )

        model = self._meta.model
        queryset = model.objects.filter(
            nome__iexact=nome,
        )

        empresa = self.empresa

        if not empresa and "empresa" in self.cleaned_data:
            empresa = self.cleaned_data.get("empresa")

        if empresa:
            queryset = queryset.filter(
                empresa=empresa,
            )

        if self.instance.pk:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise forms.ValidationError(
                "Já existe um cadastro com este nome nesta empresa."
            )

        return nome


class CargoForm(CadastroFuncionarioBaseForm):
    class Meta:
        model = Cargo
        fields = [
            "nome",
            "descricao",
            "ativo",
        ]


class NivelForm(CadastroFuncionarioBaseForm):
    class Meta:
        model = Nivel
        fields = [
            "nome",
            "ordem",
            "descricao",
            "ativo",
        ]


class EquipamentoForm(CadastroFuncionarioBaseForm):
    class Meta:
        model = Equipamento
        fields = [
            "nome",
            "descricao",
            "ativo",
        ]
