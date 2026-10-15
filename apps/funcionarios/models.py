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

    horas_abonadas = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Horas justificadas/abonadas por ferias, "
            "licencas ou afastamentos."
        ),
    )

    horas_extras_folha = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Horas extras destinadas a pagamento "
            "na folha."
        ),
    )

    horas_extras_banco = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Horas extras destinadas ao banco "
            "de horas."
        ),
    )
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
        """
        Saldo tecnico consolidado.

        Faltas/atrasos ja estao refletidos na diferenca
        entre horas realizadas/abonadas e previstas,
        portanto nao devem ser subtraidos uma segunda vez.
        """
        trabalhadas = (
            self.horas_trabalhadas
            or Decimal("0.00")
        )

        abonadas = (
            getattr(
                self,
                "horas_abonadas",
                Decimal("0.00"),
            )
            or Decimal("0.00")
        )

        extras = (
            self.horas_extras
            or Decimal("0.00")
        )

        previstas = (
            self.horas_previstas
            or Decimal("0.00")
        )

        return (
            trabalhadas
            + abonadas
            + extras
            - previstas
        ).quantize(
            Decimal("0.01")
        )

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
        """
        Calcula somente as horas extras destinadas
        ao pagamento em folha.

        Horas destinadas ao Banco de Horas nao podem
        ser pagas novamente.
        """
        if not self.folha_ponto:
            horas = Decimal("0.00")
        else:
            horas = (
                getattr(
                    self.folha_ponto,
                    "horas_extras_folha",
                    self.folha_ponto.horas_extras,
                )
                or Decimal("0.00")
            )

        fator = (
            Decimal("1.00")
            + self.adicional_percentual_hora_extra
            / Decimal("100")
        )

        return (
            horas
            * self.valor_hora
            * fator
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

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


# ============================================================
# ETAPA 8 - FUNDACAO TRABALHISTA
# ============================================================


class VinculoParceria(models.Model):
    """
    Vinculo historico entre colaborador e parceria.

    Permite rateio de um mesmo colaborador entre termos distintos,
    preservando a memoria de calculo por periodo.
    """

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="vinculos_parcerias",
    )

    termo = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        related_name="vinculos_trabalhistas",
    )

    data_inicio = models.DateField(
        verbose_name="Inicio do vinculo na parceria",
    )

    data_fim = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fim do vinculo na parceria",
    )

    percentual_rateio = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        default=Decimal("100.000"),
        verbose_name="Percentual de rateio (%)",
    )

    centro_custo = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Centro de custo",
    )

    ativo = models.BooleanField(
        default=True,
    )

    observacoes = models.TextField(
        blank=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "funcionario__nome",
            "-data_inicio",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "funcionario",
                    "termo",
                    "data_inicio",
                ],
                name="uniq_vinculo_func_termo_inicio",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        percentual_rateio__gt=0
                    )
                    & models.Q(
                        percentual_rateio__lte=100
                    )
                ),
                name="chk_vinculo_rateio_0_100",
            ),
        ]

        verbose_name = (
            "Vinculo do colaborador com a parceria"
        )

        verbose_name_plural = (
            "Vinculos dos colaboradores com as parcerias"
        )

    def clean(self):
        super().clean()

        if (
            self.data_fim
            and self.data_fim < self.data_inicio
        ):
            raise ValidationError(
                {
                    "data_fim": (
                        "A data final nao pode ser anterior "
                        "a data inicial."
                    )
                }
            )

        if (
            self.funcionario_id
            and self.termo_id
            and self.funcionario.empresa_id
            and self.termo.empresa_id
            and (
                self.funcionario.empresa_id
                != self.termo.empresa_id
            )
        ):
            raise ValidationError(
                {
                    "termo": (
                        "A parceria pertence a outra empresa."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.funcionario} - "
            f"{self.termo} - "
            f"{self.percentual_rateio}%"
        )


class EscalaTrabalho(models.Model):
    """
    Escala parametrizada e historica.

    O ciclo permite representar escalas semanais e escalas
    alternadas, inclusive 12x36, sem amarrar o sistema
    aos dias fixos da semana.
    """

    TIPO_CHOICES = (
        ("5x2", "5x2"),
        ("6x1", "6x1"),
        ("12x36", "12x36"),
        ("parcial", "Tempo parcial"),
        ("revezamento", "Revezamento"),
        ("personalizada", "Personalizada"),
    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="escalas_trabalho",
    )

    nome = models.CharField(
        max_length=120,
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default="5x2",
    )

    ciclo_dias = models.PositiveSmallIntegerField(
        default=7,
        help_text=(
            "Quantidade de dias do ciclo. "
            "Ex.: 7 para 5x2/6x1; "
            "2 para ciclo alternado 12x36."
        ),
    )

    jornada_semanal_referencia = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Jornada semanal de referencia",
    )

    data_inicio = models.DateField(
        verbose_name="Inicio da vigencia",
    )

    data_fim = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fim da vigencia",
    )

    fundamento = models.TextField(
        blank=True,
        help_text=(
            "Lei, acordo individual, ACT, CCT "
            "ou outro fundamento aplicavel."
        ),
    )

    ativo = models.BooleanField(
        default=True,
    )

    observacoes = models.TextField(
        blank=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "empresa__nome",
            "nome",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "empresa",
                    "nome",
                    "data_inicio",
                ],
                name="uniq_escala_empresa_nome_inicio",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    ciclo_dias__gte=1
                ),
                name="chk_escala_ciclo_positivo",
            ),
        ]

        verbose_name = "Escala de trabalho"
        verbose_name_plural = "Escalas de trabalho"

    def clean(self):
        super().clean()

        if (
            self.data_fim
            and self.data_fim < self.data_inicio
        ):
            raise ValidationError(
                {
                    "data_fim": (
                        "A data final nao pode ser anterior "
                        "a data inicial."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.nome} ({self.get_tipo_display()})"
        )


class JornadaEscala(models.Model):
    """
    Cada registro representa uma posicao dentro do ciclo
    da escala.

    Exemplos:

    5x2:
        ciclo 1..7
        1-5 trabalha
        6-7 descansa

    6x1:
        ciclo 1..7
        1-6 trabalha
        7 descansa

    12x36:
        ciclo 1..2
        1 trabalha 12h
        2 descansa
    """

    escala = models.ForeignKey(
        EscalaTrabalho,
        on_delete=models.CASCADE,
        related_name="jornadas_ciclo",
    )

    posicao_ciclo = models.PositiveSmallIntegerField(
        verbose_name="Posicao no ciclo",
    )

    trabalha = models.BooleanField(
        default=True,
    )

    horas_previstas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    hora_entrada = models.TimeField(
        blank=True,
        null=True,
    )

    hora_saida = models.TimeField(
        blank=True,
        null=True,
    )

    intervalo_minutos = models.PositiveIntegerField(
        default=0,
    )

    descricao = models.CharField(
        max_length=100,
        blank=True,
    )

    class Meta:
        ordering = [
            "escala",
            "posicao_ciclo",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "escala",
                    "posicao_ciclo",
                ],
                name="uniq_escala_posicao_ciclo",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    posicao_ciclo__gte=1
                ),
                name="chk_jornada_posicao_positiva",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    horas_previstas__gte=0
                ),
                name="chk_jornada_horas_nao_negativas",
            ),
        ]

        verbose_name = "Jornada da escala"
        verbose_name_plural = "Jornadas das escalas"

    def clean(self):
        super().clean()

        if (
            self.escala_id
            and self.posicao_ciclo
            > self.escala.ciclo_dias
        ):
            raise ValidationError(
                {
                    "posicao_ciclo": (
                        "A posicao nao pode ultrapassar "
                        "o tamanho do ciclo da escala."
                    )
                }
            )

        if (
            not self.trabalha
            and self.horas_previstas
            != Decimal("0.00")
        ):
            raise ValidationError(
                {
                    "horas_previstas": (
                        "Dia de descanso deve possuir "
                        "zero horas previstas."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.escala} - "
            f"dia {self.posicao_ciclo}"
        )


class EscalaFuncionario(models.Model):
    """
    Historico da escala aplicada ao trabalhador.

    data_referencia informa qual dia corresponde
    a posicao 1 do ciclo.
    """

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="historico_escalas",
    )

    escala = models.ForeignKey(
        EscalaTrabalho,
        on_delete=models.PROTECT,
        related_name="funcionarios_vinculados",
    )

    data_inicio = models.DateField(
        verbose_name="Inicio da escala",
    )

    data_fim = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fim da escala",
    )

    data_referencia = models.DateField(
        help_text=(
            "Data correspondente ao primeiro dia "
            "do ciclo da escala."
        ),
    )

    observacoes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "funcionario__nome",
            "-data_inicio",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "funcionario",
                    "data_inicio",
                ],
                name="uniq_escala_func_inicio",
            ),
        ]

        verbose_name = "Escala do colaborador"
        verbose_name_plural = "Escalas dos colaboradores"

    def clean(self):
        super().clean()

        if (
            self.data_fim
            and self.data_fim < self.data_inicio
        ):
            raise ValidationError(
                {
                    "data_fim": (
                        "A data final nao pode ser anterior "
                        "a data inicial."
                    )
                }
            )

        if (
            self.funcionario_id
            and self.escala_id
            and self.funcionario.empresa_id
            and (
                self.funcionario.empresa_id
                != self.escala.empresa_id
            )
        ):
            raise ValidationError(
                {
                    "escala": (
                        "A escala pertence a outra empresa."
                    )
                }
            )

        if (
            self.funcionario_id
            and self.data_inicio
        ):
            sobrepostos = (
                EscalaFuncionario.objects
                .filter(
                    funcionario_id=(
                        self.funcionario_id
                    )
                )
                .exclude(
                    pk=self.pk
                )
                .filter(
                    models.Q(
                        data_fim__isnull=True
                    )
                    | models.Q(
                        data_fim__gte=(
                            self.data_inicio
                        )
                    )
                )
            )

            if self.data_fim:
                sobrepostos = (
                    sobrepostos.filter(
                        data_inicio__lte=(
                            self.data_fim
                        )
                    )
                )

            if sobrepostos.exists():
                raise ValidationError(
                    {
                        "data_inicio": (
                            "Existe outra escala vigente "
                            "para este colaborador no mesmo "
                            "periodo."
                        )
                    }
                )

    def __str__(self):
        return (
            f"{self.funcionario} - {self.escala}"
        )


class RegimeBancoHoras(models.Model):
    """
    Regime juridico utilizado para compensacao
    ou banco de horas.
    """

    TIPO_CHOICES = (
        (
            "mesmo_mes",
            "Compensacao no mesmo mes",
        ),
        (
            "individual_6m",
            "Acordo individual escrito - ate 6 meses",
        ),
        (
            "coletivo",
            "Acordo ou convencao coletiva",
        ),
        (
            "personalizado",
            "Regime personalizado",
        ),
    )

    TRATAMENTO_VENCIMENTO_CHOICES = (
        (
            "pagar",
            "Pagar saldo positivo",
        ),
        (
            "compensar",
            "Compensar conforme instrumento",
        ),
        (
            "manual",
            "Analise manual",
        ),
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="regimes_banco_horas",
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
    )

    data_inicio = models.DateField()

    data_fim = models.DateField(
        blank=True,
        null=True,
    )

    prazo_compensacao_meses = (
        models.PositiveSmallIntegerField(
            blank=True,
            null=True,
        )
    )

    tratamento_vencimento = models.CharField(
        max_length=20,
        choices=TRATAMENTO_VENCIMENTO_CHOICES,
        default="pagar",
    )

    fundamento = models.TextField(
        blank=True,
    )

    referencia_documento = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Referencia ao acordo individual, "
            "ACT, CCT ou outro documento."
        ),
    )

    ativo = models.BooleanField(
        default=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "funcionario__nome",
            "-data_inicio",
        ]

        verbose_name = "Regime de banco de horas"
        verbose_name_plural = "Regimes de banco de horas"

    def clean(self):
        super().clean()

        if (
            self.data_fim
            and self.data_fim < self.data_inicio
        ):
            raise ValidationError(
                {
                    "data_fim": (
                        "A data final nao pode ser anterior "
                        "a data inicial."
                    )
                }
            )

        if (
            self.tipo == "individual_6m"
            and (
                not self.prazo_compensacao_meses
                or self.prazo_compensacao_meses > 6
            )
        ):
            raise ValidationError(
                {
                    "prazo_compensacao_meses": (
                        "O acordo individual escrito "
                        "deve observar prazo de ate 6 meses."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.funcionario} - "
            f"{self.get_tipo_display()}"
        )


class MovimentoBancoHoras(models.Model):
    """
    Extrato auditavel do banco de horas.

    O saldo nao e gravado como numero solto:
    ele deve ser reconstruivel pelos movimentos.
    """

    TIPO_CHOICES = (
        ("credito", "Credito"),
        ("debito", "Debito"),
        ("ajuste_credito", "Ajuste de credito"),
        ("ajuste_debito", "Ajuste de debito"),
        ("pagamento", "Pagamento em folha"),
        ("liquidacao", "Liquidacao"),
    )

    ORIGEM_CHOICES = (
        ("ponto", "Folha/ponto"),
        ("compensacao", "Compensacao"),
        ("folga", "Folga"),
        ("ajuste", "Ajuste autorizado"),
        ("rescisao", "Rescisao"),
        ("folha", "Folha de pagamento"),
        ("outro", "Outro"),
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="movimentos_banco_horas",
    )

    regime = models.ForeignKey(
        RegimeBancoHoras,
        on_delete=models.PROTECT,
        related_name="movimentos",
    )

    data = models.DateField()

    competencia = models.DateField(
        help_text="Primeiro dia do mes.",
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
    )

    origem = models.CharField(
        max_length=20,
        choices=ORIGEM_CHOICES,
        default="ponto",
    )

    horas = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    descricao = models.CharField(
        max_length=255,
        blank=True,
    )

    referencia_origem = models.CharField(
        max_length=100,
        blank=True,
        help_text=(
            "Identificador do ponto, folha, "
            "rescisao ou ajuste que originou "
            "o movimento."
        ),
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    criado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="movimentos_banco_horas_criados",
    )

    class Meta:
        ordering = [
            "funcionario__nome",
            "data",
            "id",
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    horas__gt=0
                ),
                name="chk_mov_banco_horas_positivo",
            ),
            models.UniqueConstraint(
                fields=[
                    "referencia_origem",
                ],
                condition=~models.Q(
                    referencia_origem=""
                ),
                name="uniq_mov_banco_referencia_origem",
            ),
        ]

        verbose_name = "Movimento de banco de horas"
        verbose_name_plural = "Movimentos de banco de horas"

    def clean(self):
        super().clean()

        if (
            self.regime_id
            and self.funcionario_id
            and (
                self.regime.funcionario_id
                != self.funcionario_id
            )
        ):
            raise ValidationError(
                {
                    "regime": (
                        "O regime de banco de horas deve "
                        "pertencer ao mesmo colaborador."
                    )
                }
            )

        if self.competencia:
            if self.competencia.day != 1:
                raise ValidationError(
                    {
                        "competencia": (
                            "A competencia deve usar "
                            "o primeiro dia do mes."
                        )
                    }
                )

    @property
    def horas_com_sinal(self):
        debitos = {
            "debito",
            "ajuste_debito",
            "pagamento",
            "liquidacao",
        }

        if self.tipo in debitos:
            return -self.horas

        return self.horas

    def __str__(self):
        return (
            f"{self.funcionario} - "
            f"{self.data:%d/%m/%Y} - "
            f"{self.get_tipo_display()}"
        )


# ============================================================
# ETAPA 8.4B - FERIAS, LICENCAS E AFASTAMENTOS
# ============================================================


class TipoAfastamento(models.Model):
    """
    Cadastro parametrizado dos tipos de licenca,
    ausencia justificada e afastamento.

    Os efeitos sao cadastrados e versionados, evitando
    hardcode de regras que podem depender de lei,
    ACT, CCT, categoria ou vigencia.
    """

    codigo = models.SlugField(
        max_length=60,
    )

    nome = models.CharField(
        max_length=120,
    )

    descricao = models.TextField(
        blank=True,
    )

    data_inicio_vigencia = models.DateField()

    data_fim_vigencia = models.DateField(
        blank=True,
        null=True,
    )

    abona_ponto = models.BooleanField(
        default=False,
        help_text=(
            "Indica se a ausencia nao deve ser "
            "tratada como falta na folha de ponto."
        ),
    )

    remunerado = models.BooleanField(
        default=False,
    )

    computa_ferias = models.BooleanField(
        default=True,
        help_text=(
            "Parametro operacional. O efeito final "
            "deve observar a legislacao aplicavel."
        ),
    )

    computa_decimo_terceiro = models.BooleanField(
        default=True,
        help_text=(
            "Parametro operacional sujeito a regra "
            "legal/previdenciaria aplicavel."
        ),
    )

    incide_fgts = models.BooleanField(
        default=False,
    )

    incide_inss = models.BooleanField(
        default=False,
    )

    exige_documento = models.BooleanField(
        default=False,
    )

    documento_sensivel = models.BooleanField(
        default=False,
        help_text=(
            "Use para documentos de saude ou outros "
            "dados pessoais sensiveis."
        ),
    )

    fundamento = models.TextField(
        blank=True,
        help_text=(
            "Lei, CLT, norma previdenciaria, "
            "ACT, CCT ou outro fundamento."
        ),
    )

    ativo = models.BooleanField(
        default=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "nome",
            "-data_inicio_vigencia",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "codigo",
                    "data_inicio_vigencia",
                ],
                name="uniq_tipo_afast_codigo_vigencia",
            ),
        ]

        verbose_name = "Tipo de afastamento"
        verbose_name_plural = "Tipos de afastamento"

    def clean(self):
        super().clean()

        if (
            self.data_fim_vigencia
            and self.data_fim_vigencia
            < self.data_inicio_vigencia
        ):
            raise ValidationError(
                {
                    "data_fim_vigencia": (
                        "A vigencia final nao pode ser "
                        "anterior a inicial."
                    )
                }
            )

    def __str__(self):
        return self.nome


class AfastamentoFuncionario(models.Model):
    """
    Registra licencas, atestados e outros afastamentos
    de forma historica.

    Nao mistura afastamento com falta injustificada.
    """

    STATUS_CHOICES = (
        ("rascunho", "Rascunho"),
        ("confirmado", "Confirmado"),
        ("cancelado", "Cancelado"),
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="afastamentos",
    )

    tipo = models.ForeignKey(
        TipoAfastamento,
        on_delete=models.PROTECT,
        related_name="afastamentos",
    )

    data_inicio = models.DateField()

    data_fim = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="rascunho",
    )

    referencia_documento = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Referencia segura ao documento. "
            "Nao registrar diagnostico medico aqui."
        ),
    )

    observacoes = models.TextField(
        blank=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    criado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="afastamentos_funcionarios_criados",
    )

    class Meta:
        ordering = [
            "funcionario__nome",
            "-data_inicio",
        ]

        verbose_name = "Afastamento do colaborador"
        verbose_name_plural = "Afastamentos dos colaboradores"

    def clean(self):
        super().clean()

        if (
            self.data_inicio
            and self.data_fim
            and self.data_fim < self.data_inicio
        ):
            raise ValidationError(
                {
                    "data_fim": (
                        "A data final nao pode ser anterior "
                        "a data inicial."
                    )
                }
            )

        if (
            self.funcionario_id
            and self.data_inicio
            and self.funcionario.data_admissao
            and self.data_inicio
            < self.funcionario.data_admissao
        ):
            raise ValidationError(
                {
                    "data_inicio": (
                        "O afastamento nao pode iniciar "
                        "antes da admissao."
                    )
                }
            )

        if (
            self.funcionario_id
            and self.data_fim
            and self.funcionario.data_desligamento
            and self.data_fim
            > self.funcionario.data_desligamento
        ):
            raise ValidationError(
                {
                    "data_fim": (
                        "O afastamento nao pode terminar "
                        "apos o desligamento."
                    )
                }
            )

        if (
            self.funcionario_id
            and self.data_inicio
            and self.data_fim
            and self.status != "cancelado"
        ):
            sobrepostos = (
                AfastamentoFuncionario.objects
                .filter(
                    funcionario_id=self.funcionario_id,
                )
                .exclude(
                    pk=self.pk,
                )
                .exclude(
                    status="cancelado",
                )
                .filter(
                    data_inicio__lte=self.data_fim,
                    data_fim__gte=self.data_inicio,
                )
            )

            if sobrepostos.exists():
                raise ValidationError(
                    {
                        "data_inicio": (
                            "Existe outro afastamento "
                            "no mesmo periodo."
                        )
                    }
                )

    @property
    def quantidade_dias(self):
        if (
            not self.data_inicio
            or not self.data_fim
        ):
            return 0

        return (
            self.data_fim
            - self.data_inicio
        ).days + 1

    def __str__(self):
        return (
            f"{self.funcionario} - "
            f"{self.tipo} - "
            f"{self.data_inicio:%d/%m/%Y}"
        )


class PeriodoAquisitivoFerias(models.Model):
    """
    Representa o periodo aquisitivo individual.

    Os valores financeiros permanecem separados
    desta estrutura e serao calculados pelo motor
    financeiro em etapa posterior.
    """

    STATUS_CHOICES = (
        ("aberto", "Aberto"),
        ("adquirido", "Adquirido"),
        ("parcialmente_gozado", "Parcialmente gozado"),
        ("gozado", "Gozado"),
        ("encerrado", "Encerrado"),
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="periodos_aquisitivos_ferias",
    )

    data_inicio = models.DateField()

    data_fim = models.DateField()

    data_limite_concessao = models.DateField(
        blank=True,
        null=True,
    )

    dias_direito = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("30.00"),
    )

    dias_gozados = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    dias_abono = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="aberto",
    )

    observacoes = models.TextField(
        blank=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "funcionario__nome",
            "-data_inicio",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "funcionario",
                    "data_inicio",
                    "data_fim",
                ],
                name="uniq_periodo_aquisitivo_ferias",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    dias_direito__gte=0
                ),
                name="chk_ferias_dias_direito",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    dias_gozados__gte=0
                ),
                name="chk_ferias_dias_gozados",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    dias_abono__gte=0
                ),
                name="chk_ferias_dias_abono",
            ),
        ]

        verbose_name = "Periodo aquisitivo de ferias"
        verbose_name_plural = "Periodos aquisitivos de ferias"

    def clean(self):
        super().clean()

        if (
            self.data_fim
            and self.data_inicio
            and self.data_fim < self.data_inicio
        ):
            raise ValidationError(
                {
                    "data_fim": (
                        "A data final nao pode ser anterior "
                        "a data inicial."
                    )
                }
            )

        if (
            self.dias_gozados is not None
            and self.dias_abono is not None
            and self.dias_direito is not None
            and (
                self.dias_gozados
                + self.dias_abono
                > self.dias_direito
            )
        ):
            raise ValidationError(
                {
                    "dias_gozados": (
                        "Dias gozados mais abono nao podem "
                        "superar os dias de direito."
                    )
                }
            )

    @property
    def saldo_dias(self):
        return (
            (self.dias_direito or Decimal("0.00"))
            - (self.dias_gozados or Decimal("0.00"))
            - (self.dias_abono or Decimal("0.00"))
        )

    def __str__(self):
        return (
            f"{self.funcionario} - "
            f"{self.data_inicio:%d/%m/%Y} a "
            f"{self.data_fim:%d/%m/%Y}"
        )


class FeriasFuncionario(models.Model):
    """
    Periodo efetivo de gozo de ferias.

    O gozo altera a situacao da folha de ponto,
    mas nao deve ser tratado como falta.
    """

    STATUS_CHOICES = (
        ("programada", "Programada"),
        ("confirmada", "Confirmada"),
        ("gozada", "Gozada"),
        ("cancelada", "Cancelada"),
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="ferias_historico",
    )

    periodo_aquisitivo = models.ForeignKey(
        PeriodoAquisitivoFerias,
        on_delete=models.PROTECT,
        related_name="gozos",
    )

    data_inicio = models.DateField()

    data_fim = models.DateField()

    dias_gozo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    dias_abono = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    data_pagamento = models.DateField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="programada",
    )

    observacoes = models.TextField(
        blank=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    criado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="ferias_funcionarios_criadas",
    )

    class Meta:
        ordering = [
            "funcionario__nome",
            "-data_inicio",
        ]

        verbose_name = "Ferias do colaborador"
        verbose_name_plural = "Ferias dos colaboradores"

    def clean(self):
        super().clean()

        if (
            self.data_inicio
            and self.data_fim
            and self.data_fim < self.data_inicio
        ):
            raise ValidationError(
                {
                    "data_fim": (
                        "A data final nao pode ser anterior "
                        "a data inicial."
                    )
                }
            )

        if (
            self.funcionario_id
            and self.periodo_aquisitivo_id
            and (
                self.periodo_aquisitivo.funcionario_id
                != self.funcionario_id
            )
        ):
            raise ValidationError(
                {
                    "periodo_aquisitivo": (
                        "O periodo aquisitivo pertence "
                        "a outro colaborador."
                    )
                }
            )

        if (
            self.data_inicio
            and self.data_fim
            and self.dias_gozo is not None
        ):
            dias_calendario = (
                self.data_fim
                - self.data_inicio
            ).days + 1

            if (
                self.dias_gozo
                != Decimal(
                    str(dias_calendario)
                )
            ):
                raise ValidationError(
                    {
                        "dias_gozo": (
                            "Os dias de gozo devem corresponder "
                            "ao periodo informado."
                        )
                    }
                )

        if (
            self.funcionario_id
            and self.data_inicio
            and self.data_fim
            and self.status != "cancelada"
        ):
            sobrepostas = (
                FeriasFuncionario.objects
                .filter(
                    funcionario_id=self.funcionario_id,
                )
                .exclude(
                    pk=self.pk,
                )
                .exclude(
                    status="cancelada",
                )
                .filter(
                    data_inicio__lte=self.data_fim,
                    data_fim__gte=self.data_inicio,
                )
            )

            if sobrepostas.exists():
                raise ValidationError(
                    {
                        "data_inicio": (
                            "Existe outro periodo de ferias "
                            "sobreposto."
                        )
                    }
                )

    def __str__(self):
        return (
            f"{self.funcionario} - "
            f"{self.data_inicio:%d/%m/%Y} a "
            f"{self.data_fim:%d/%m/%Y}"
        )


# ============================================================
# ETAPA 8.4C - CALENDARIO DIARIO DA FOLHA DE PONTO
# ============================================================


class DiaFolhaPonto(models.Model):
    """
    Representa cada dia de uma competencia da folha de ponto.

    A situacao do dia e derivada de:
    - periodo contratual;
    - ferias;
    - afastamentos/licencas;
    - escala vigente.

    Marcacoes efetivas serao tratadas em etapa posterior.
    """

    TIPO_DIA_CHOICES = (
        ("fora_vinculo", "Fora do vinculo"),
        ("trabalho", "Trabalho previsto"),
        ("descanso", "Descanso"),
        ("ferias", "Ferias"),
        (
            "afastamento_abonado",
            "Afastamento/licenca abonado",
        ),
        (
            "afastamento_nao_abonado",
            "Afastamento/licenca nao abonado",
        ),
        (
            "sem_configuracao",
            "Sem configuracao de jornada",
        ),
    )

    folha_ponto = models.ForeignKey(
        FolhaPonto,
        on_delete=models.CASCADE,
        related_name="dias",
    )

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="dias_folha_ponto",
    )

    data = models.DateField()

    tipo_dia = models.CharField(
        max_length=40,
        choices=TIPO_DIA_CHOICES,
    )

    escala = models.ForeignKey(
        EscalaTrabalho,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="dias_folha_ponto",
    )

    jornada_escala = models.ForeignKey(
        JornadaEscala,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="dias_folha_ponto",
    )

    ferias = models.ForeignKey(
        FeriasFuncionario,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="dias_folha_ponto",
    )

    afastamento = models.ForeignKey(
        AfastamentoFuncionario,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="dias_folha_ponto",
    )

    horas_previstas = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    horas_abonadas = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    horas_trabalhadas = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    horas_extras = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    horas_faltas_atrasos = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    saldo_banco_candidato = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Saldo tecnico do dia. Ainda nao significa "
            "credito ou debito definitivo no banco de horas."
        ),
    )

    TRATAMENTO_SALDO_CHOICES = (
        ("pendente", "Pendente"),
        ("folha", "Folha de pagamento"),
        ("banco", "Banco de horas"),
        ("sem_saldo", "Sem saldo"),
    )

    tratamento_saldo = models.CharField(
        max_length=20,
        choices=TRATAMENTO_SALDO_CHOICES,
        default="pendente",
    )

    entrada_1 = models.TimeField(
        blank=True,
        null=True,
    )

    saida_1 = models.TimeField(
        blank=True,
        null=True,
    )

    entrada_2 = models.TimeField(
        blank=True,
        null=True,
    )

    saida_2 = models.TimeField(
        blank=True,
        null=True,
    )

    observacoes = models.TextField(
        blank=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "folha_ponto",
            "data",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "folha_ponto",
                    "data",
                ],
                name="uniq_folha_ponto_dia",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    horas_previstas__gte=0
                ),
                name="chk_dia_ponto_previstas",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    horas_abonadas__gte=0
                ),
                name="chk_dia_ponto_abonadas",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    horas_trabalhadas__gte=0
                ),
                name="chk_dia_ponto_trabalhadas",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    horas_extras__gte=0
                ),
                name="chk_dia_ponto_extras",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    horas_faltas_atrasos__gte=0
                ),
                name="chk_dia_ponto_faltas",
            ),
        ]

        verbose_name = "Dia da folha de ponto"
        verbose_name_plural = "Dias da folha de ponto"

    def clean(self):
        super().clean()

        if (
            self.folha_ponto_id
            and self.funcionario_id
            and (
                self.folha_ponto.funcionario_id
                != self.funcionario_id
            )
        ):
            raise ValidationError(
                {
                    "funcionario": (
                        "O colaborador deve ser o mesmo "
                        "da folha de ponto."
                    )
                }
            )

        if (
            self.tipo_dia == "ferias"
            and not self.ferias_id
        ):
            raise ValidationError(
                {
                    "ferias": (
                        "Dia classificado como ferias "
                        "deve possuir periodo vinculado."
                    )
                }
            )

        if (
            self.tipo_dia.startswith("afastamento")
            and not self.afastamento_id
        ):
            raise ValidationError(
                {
                    "afastamento": (
                        "Dia de afastamento deve possuir "
                        "registro vinculado."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.funcionario} - "
            f"{self.data:%d/%m/%Y} - "
            f"{self.get_tipo_dia_display()}"
        )
