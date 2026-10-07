from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.contrib.auth.models import User
from django.urls import reverse
from apps.departamentos.models import Departamento
from apps.core.models import SequenciaPseudonimo
from apps.core.documentos_fiscais import documento_cpf_normalizado
from apps.empresas.models import Empresa
from apps.curso.models import Curso
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP


def get_absolute_url():
    return reverse('list_funcionarios')


class CadastroFuncionarioBase(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="%(class)ss",
    )
    nome = models.CharField(
        max_length=120,
    )
    descricao = models.TextField(
        blank=True,
    )
    ativo = models.BooleanField(
        default=True,
    )

    class Meta:
        abstract = True
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Cargo(CadastroFuncionarioBase):
    class Meta(CadastroFuncionarioBase.Meta):
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "nome"],
                name="uniq_cargo_empresa_nome",
            ),
        ]


class Nivel(CadastroFuncionarioBase):
    ordem = models.PositiveIntegerField(
        default=0,
    )

    class Meta(CadastroFuncionarioBase.Meta):
        verbose_name = "Nível"
        verbose_name_plural = "Níveis"
        ordering = ["ordem", "nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "nome"],
                name="uniq_nivel_empresa_nome",
            ),
        ]


class Equipamento(CadastroFuncionarioBase):
    class Meta(CadastroFuncionarioBase.Meta):
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "nome"],
                name="uniq_equipamento_empresa_nome",
            ),
        ]


class Funcionario(models.Model):

    class Meta:
        ordering = ["nome"]
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"

        permissions = [
            (
                "view_funcionario_identificacao",
                "Pode visualizar identificacao e vinculo do colaborador",
            ),
            (
                "change_funcionario_identificacao",
                "Pode alterar identificacao e vinculo do colaborador",
            ),
            (
                "view_funcionario_dados_pessoais",
                "Pode visualizar dados pessoais do colaborador",
            ),
            (
                "change_funcionario_dados_pessoais",
                "Pode alterar dados pessoais do colaborador",
            ),
            (
                "view_funcionario_endereco",
                "Pode visualizar endereco do colaborador",
            ),
            (
                "change_funcionario_endereco",
                "Pode alterar endereco do colaborador",
            ),
            (
                "view_funcionario_dados_funcionais",
                "Pode visualizar dados funcionais do colaborador",
            ),
            (
                "change_funcionario_dados_funcionais",
                "Pode alterar dados funcionais do colaborador",
            ),
            (
                "view_funcionario_folha",
                "Pode visualizar dados de folha e bancarios do colaborador",
            ),
            (
                "change_funcionario_folha",
                "Pode alterar dados de folha e bancarios do colaborador",
            ),
            (
                "view_funcionario_acesso_sistema",
                "Pode visualizar acesso ao sistema do colaborador",
            ),
            (
                "change_funcionario_acesso_sistema",
                "Pode alterar acesso ao sistema do colaborador",
            ),
        ]

    nome = models.CharField(max_length=100, verbose_name='Colaborador')
    usuario = models.CharField(max_length=100, verbose_name='Usuario')
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="colaboradores",
        verbose_name="Cargo",
    )
    nivel = models.ForeignKey(
        Nivel,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="colaboradores",
        verbose_name="Nível",
    )
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="colaboradores",
        verbose_name="Equipamento",
    )

    endereco = models.CharField(max_length=100, verbose_name='Endereço')
    bairro = models.CharField(max_length=100, verbose_name='Bairro')
    cep = models.CharField(max_length=100, verbose_name='CEP')
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=100, verbose_name='Estado')
    email = models.CharField(max_length=100, verbose_name='E-mail')
    Telefone = models.CharField(max_length=100, verbose_name='Telefone')


    salarioBase = models.DecimalField(max_digits=10, decimal_places=2,  blank=True, null=True, verbose_name='Salário Base')
    salarioBruto = models.DecimalField(max_digits=10, decimal_places=2,  blank=True, null=True, verbose_name='Salário Bruto')
    salarioLiquido = models.DecimalField(max_digits=10, decimal_places=2,  blank=True, null=True, verbose_name='Salário Líquido')
    diasTrabalhados = models.CharField(max_length=10,  blank=True, null=True, verbose_name='Dias Trabalhados')
    avisoPrevio = models.DecimalField(max_digits=10, decimal_places=2,   blank=True, null=True, verbose_name='Aviso Prévio')
    avosFerias = models.DecimalField(max_digits=10, decimal_places=2,   blank=True, null=True, verbose_name='1/12 avos Férias')
    avosTercoFerias = models.DecimalField(max_digits=10, decimal_places=2,   blank=True, null=True, verbose_name='1/12 avos 1/3 Férias')
    avos13Salario = models.DecimalField(max_digits=10, decimal_places=2,   blank=True, null=True, verbose_name='1/12 avos 13º Salário')
    fgts = models.DecimalField(max_digits=10, decimal_places=2,   blank=True, null=True, verbose_name='FGTS')
    multafgts = models.DecimalField(max_digits=10, decimal_places=2,   blank=True, null=True, verbose_name='Multa FGTS')
    inss = models.DecimalField(max_digits=10, decimal_places=2,   blank=True, null=True, verbose_name='INSS')
    totalVerbaRescisoria = models.DecimalField(max_digits=10, decimal_places=2,   blank=True, null=True, verbose_name='Total Verba Rescisória')
    totalRescisao = models.DecimalField(max_digits=10, decimal_places=2,   blank=True, null=True, verbose_name='Total Rescisão')



    # Sprint 17 — dados do vínculo com a parceria
    TIPO_VINCULO_CHOICES = (
        ("clt", "Empregado CLT"),
        ("autonomo", "Autônomo / contribuinte individual"),
        ("estagiario", "Estagiário"),
        ("bolsista", "Bolsista"),
        ("voluntario", "Voluntário"),
        ("dirigente_remunerado", "Dirigente remunerado"),
        ("dirigente_nao_remunerado", "Dirigente não remunerado"),
        ("outro", "Outro"),
    )
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name="CPF")
    cpf_normalizado = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        unique=True,
        editable=False,
        verbose_name="CPF normalizado",
    )
    codigo_pseudonimo = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        editable=False,
        verbose_name="Código pseudonimizado",
    )
    pis_pasep_nit = models.CharField(max_length=20, blank=True, null=True, verbose_name="PIS/PASEP/NIT")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de nascimento")
    tipo_vinculo = models.CharField(max_length=30, choices=TIPO_VINCULO_CHOICES, default="clt", verbose_name="Tipo de vínculo")
    data_admissao = models.DateField(blank=True, null=True, verbose_name="Data de admissão")
    data_desligamento = models.DateField(blank=True, null=True, verbose_name="Data de desligamento")
    jornada_semanal = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("44.00"), verbose_name="Jornada semanal")
    divisor_mensal = models.PositiveIntegerField(default=220, verbose_name="Divisor mensal")
    termo = models.ForeignKey("termos.Termos", on_delete=models.PROTECT, blank=True, null=True, related_name="trabalhadores", verbose_name="Termo/parceria")
    centro_custo = models.CharField(max_length=120, blank=True, null=True, verbose_name="Centro de custo")
    banco = models.CharField(max_length=80, blank=True, null=True, verbose_name="Banco")
    agencia = models.CharField(max_length=20, blank=True, null=True, verbose_name="Agência")
    conta_bancaria = models.CharField(max_length=30, blank=True, null=True, verbose_name="Conta bancária")

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    curso = models.ManyToManyField(Curso, verbose_name='Cursos Realizados')
    # curso = models.ForeignKey(
    #     Curso, on_delete=models.PROTECT, null=True, blank=True)  # ok
    departamentos = models.ManyToManyField(Departamento)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, null=True, blank=True)
    imagem = models.ImageField()
    de_ferias = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    def _validar_identidade_pseudonima(self):
        precisa_validar = (
            not self.codigo_pseudonimo
            or self.cpf_normalizado is not None
        )

        if not precisa_validar:
            # Registro legado preservado ate saneamento posterior.
            return

        try:
            cpf = documento_cpf_normalizado(self.cpf)
        except ValueError as exc:
            raise ValidationError(
                {
                    "cpf": (
                        "CPF obrigatorio e valido para "
                        "identificacao pseudonimizada."
                    )
                }
            ) from exc

        if self.pk and self.codigo_pseudonimo:
            anterior = (
                type(self).objects
                .filter(pk=self.pk)
                .values_list(
                    "cpf_normalizado",
                    flat=True,
                )
                .first()
            )

            if anterior and anterior != cpf:
                raise ValidationError(
                    {
                        "cpf": (
                            "O CPF associado ao codigo "
                            "pseudonimizado nao pode ser alterado."
                        )
                    }
                )

        duplicado = (
            type(self).objects
            .exclude(pk=self.pk)
            .filter(cpf_normalizado=cpf)
            .exists()
        )

        if duplicado:
            raise ValidationError(
                {
                    "cpf": (
                        "Este CPF ja possui um colaborador "
                        "pseudonimizado."
                    )
                }
            )

        self.cpf_normalizado = cpf

    def clean(self):
        super().clean()
        self._validar_identidade_pseudonima()

    def save(self, *args, **kwargs):
        self._validar_identidade_pseudonima()

        with transaction.atomic():
            if not self.codigo_pseudonimo:
                self.codigo_pseudonimo = (
                    SequenciaPseudonimo.proximo_codigo(
                        SequenciaPseudonimo.Tipo.COLABORADOR
                    )
                )

            return super().save(*args, **kwargs)

    @property
    def total_horas_extra(self):
        total = self.registrohoraextra_set.filter(utilizada=False).aggregate(
            Sum('horas'))['horas__sum']
        return total or 0

    def __str__(self):  # ok
        return self.nome  # ok


class FolhaPonto(models.Model):
    STATUS_CHOICES = (("aberta", "Aberta"), ("fechada", "Fechada"))
    funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name="folhas_ponto")
    competencia = models.DateField(help_text="Use o primeiro dia do mês.", verbose_name="Competência")
    horas_previstas = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal("0.00"))
    horas_trabalhadas = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal("0.00"))
    horas_extras = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal("0.00"))
    horas_faltas_atrasos = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal("0.00"), verbose_name="Faltas/atrasos (horas)")
    banco_horas = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal("0.00"))
    observacoes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="aberta")
    fechado_em = models.DateTimeField(blank=True, null=True)
    fechado_por = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name="folhas_ponto_fechadas")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-competencia", "funcionario__nome"]
        constraints = [models.UniqueConstraint(fields=["funcionario", "competencia"], name="uniq_ponto_func_competencia")]
        verbose_name = "Folha de ponto"
        verbose_name_plural = "Folhas de ponto"

    @property
    def saldo_horas(self):
        return (self.horas_trabalhadas + self.horas_extras - self.horas_previstas - self.horas_faltas_atrasos).quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.funcionario} - {self.competencia:%m/%Y}"


class FolhaPagamento(models.Model):
    STATUS_CHOICES = (("rascunho", "Rascunho"), ("fechada", "Fechada"))
    funcionario = models.ForeignKey(Funcionario, on_delete=models.PROTECT, related_name="folhas_pagamento")
    folha_ponto = models.OneToOneField(FolhaPonto, on_delete=models.PROTECT, blank=True, null=True, related_name="contracheque")
    competencia = models.DateField(help_text="Use o primeiro dia do mês.", verbose_name="Competência")
    salario_base = models.DecimalField(max_digits=12, decimal_places=2)
    adicional_percentual_hora_extra = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("50.00"), verbose_name="Adicional de hora extra (%)")
    outras_verbas = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="Outros proventos")
    outros_descontos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    inss = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="INSS")
    irrf = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="IRRF")
    vale_transporte = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    pensao = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), verbose_name="Pensão")
    observacoes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="rascunho")
    fechado_em = models.DateTimeField(blank=True, null=True)
    fechado_por = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name="folhas_pagamento_fechadas")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-competencia", "funcionario__nome"]
        constraints = [models.UniqueConstraint(fields=["funcionario", "competencia"], name="uniq_pagamento_func_competencia")]
        verbose_name = "Folha de pagamento"
        verbose_name_plural = "Folhas de pagamento"

    def _d(self, valor):
        return (valor or Decimal("0.00"))

    @property
    def valor_hora(self):
        divisor = self.funcionario.divisor_mensal or 220
        return (self.salario_base / Decimal(divisor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def valor_horas_extras(self):
        horas = self.folha_ponto.horas_extras if self.folha_ponto else Decimal("0.00")
        fator = Decimal("1.00") + self.adicional_percentual_hora_extra / Decimal("100")
        return (horas * self.valor_hora * fator).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def desconto_faltas_atrasos(self):
        horas = self.folha_ponto.horas_faltas_atrasos if self.folha_ponto else Decimal("0.00")
        return (horas * self.valor_hora).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def total_proventos(self):
        return (self.salario_base + self.valor_horas_extras + self._d(self.outras_verbas)).quantize(Decimal("0.01"))

    @property
    def total_descontos(self):
        return (self.desconto_faltas_atrasos + self._d(self.inss) + self._d(self.irrf) + self._d(self.vale_transporte) + self._d(self.pensao) + self._d(self.outros_descontos)).quantize(Decimal("0.01"))

    @property
    def valor_liquido(self):
        return (self.total_proventos - self.total_descontos).quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.funcionario} - {self.competencia:%m/%Y}"
