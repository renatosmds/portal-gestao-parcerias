from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from apps.departamentos.models import Departamento
from apps.empresas.models import Empresa
from apps.curso.models import Curso
from apps.conferencia3.models import Conferencia3
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP


def get_absolute_url():
    return reverse('list_funcionarios')


class Funcionario(models.Model):

    class Meta:
        ordering = ["nome"]

    CARGO_CHOICES = (
        (u'--', u'--'),
        (u'administrador(a)', u'Administrador(a)'),
        (u'administrador(a) do Sistema', u'Administrador(a) do Sistema'),
        (u'almoxarife', u'Almoxarife'),
        (u'analista de comunicação', u'Analista de Comunicação'),
        (u'analista de processos', u'Analista de Processos'),
        (u'assistente administrativo', u'Assistente Administrativo'),
        (u'assistente de rh', u'Assistente de RH'),
        (u'atendente de restaurante', u'Atendente de Restaurante'),
        (u'auxiliar de coordenação', u'Auxiliar de Coordenação'),
        (u'auxiliar de cozinha', u'Auxiliar de Cozinha'),
        (u'auxiliar de escritório', u'Auxiliar de Escritório'),
        (u'auxiliar de serviços gerais', u'Auxiliar de Serviços Gerais'),
        (u'caixa', u'Caixa'),
        (u'chefe de cozinha', u'Chefe de Cozinha'),
        (u'comissionado(a)', u'Comissionado(a)'),
        (u'contratado(a)', u'Contratado(a)'),
        (u'coordenador(a)', u'Coordenador(a)'),
        (u'coordenador(a) administrativo financeiro', u'Coordenador(a) Administrativo Financeiro'),
        (u'coordenador(a) de eventos', u'Coordenador(a) de Eventos'),
        (u'coordenador(a) de logística', u'Coordenador(a) de logística'),
        (u'coordenador(a) de projetos', u'Coordenador(a) de Projetos'),
        (u'cozinheiro(a)', u'Cozinheiro(a)'),
        (u'diretor(a) de abastecimento', u'Diretor(a) de Abastecimento'),
        (u'efetivo(a)', u'Efetivo(a)'),
        (u'encarregado(a) de manutenção', u'Encarregado(a) de Manutenção'),
        (u'gerente administrativo', u'Gerente Administrativo'),
        (u'gerente administrativo financeiro', u'Gerente Administrativo Financeiro'),
        (u'gerente de prestação de contas', u'Gerente de Prestação de Contas'),
        (u'gerente de qualidade', u'Gerente de Qualidade'),
        (u'gerente financeiro', u'Gerente Financeiro'),
        (u'gestor(a)', u'Gestor(a)'),
        (u'motorista', u'Motorista'),
        (u'nutricionista', u'Nutricionista'),
        (u'operador(a) de manutenção', u'Operador(a) de Manutenção'),
        (u'político', u'Político'),
        (u'saladeira(o)', u'Saladeira(o)'),
        (u'supervisor(a) de manutenção', u'Supervisor(a) de Manutenção'),
        (u'supervisor(a) de serviços gerais', u'Supervisor(a) de Serviços Gerais'),
        (u'técnico de contabilidade', u'Técnico de Contabilidade'),
    )

    NIVEL_CHOICES = (u'--', u'--'), (u'i', u'I'), (u'ii', u'II'), (u'iii', u'III'), (u'iv', u'IV'), (u'v', u'V'), \
                    (u'vi', u'VI'), (u'vii', u'VII'), (u'viii', u'VIII'), (u'ix', u'IX'), (u'x', u'X'), (u'xi', u'XI'),\
                    (u'xii', u'XII'), (u'dam 01', u'DAM 01'), (u'dam 02', u'DAM 02'), (u'dam 03', u'DAM 03'), \
                    (u'dam 04', u'DAM 04'), (u'dam 05', u'DAM 05'), (u'dam 06', u'DAM 06'), (u'dam 07', u'DAM 07'), \
                    (u'dam 08', u'DAM 08'), (u'dam 09', u'DAM 09'), (u'dam 10', u'DAM 10'), (u'dam 11', u'DAM 11'), \
                    (u'dam 12', u'DAM 12'), (u'dam 13', u'DAM 13'), (u'dam 14', u'DAM 14'), (u'dam 15', u'DAM 15'), \
                    (u'dam 16', u'DAM 16'), (u'dam 17', u'DAM 17'), (u'dam 18', u'DAM 18'), (u'dam 19', u'DAM 19'), \
                    (u'dam 20', u'DAM 20')

    EQUIPAMENTO_CHOICES = (u'--', u'--'), (u'cozinha comunitária nacional', u'Cozinha Comunitária Nacional'), \
                          (u'cozinha comunitária nova contagem', u'Cozinha Comunitária Nova Contagem'),\
                          (u'restaurante popular eldorado', u'Restaurante Popular Eldorado'),\
                          (u'restaurante popular nova contagem', u'Restaurante Popular Nova Contagem'),\
                          (u'restaurante popular ressaca', u'Restaurante Popular Ressaca')

    nome = models.CharField(max_length=100, verbose_name='Credor')
    usuario = models.CharField(max_length=100, verbose_name='Usuario')
    cargo = models.CharField(max_length=100, choices=CARGO_CHOICES, blank=True, null=True, verbose_name='Cargo')
    nivel = models.CharField(max_length=10, choices=NIVEL_CHOICES, blank=True, null=True, verbose_name='Nível')
    equipamento = models.CharField(max_length=100, choices=EQUIPAMENTO_CHOICES, blank=True, null=True, verbose_name='Equipamento')
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

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    curso = models.ManyToManyField(Curso, verbose_name='Cursos Realizados')
    conferencia3 = models.ManyToManyField(Conferencia3, verbose_name='Cursos Realizados')
    # curso = models.ForeignKey(
    #     Curso, on_delete=models.PROTECT, null=True, blank=True)  # ok
    departamentos = models.ManyToManyField(Departamento)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, null=True, blank=True)
    imagem = models.ImageField()
    de_ferias = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

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
