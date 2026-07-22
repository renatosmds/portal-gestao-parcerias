from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from apps.departamentos.models import Departamento
from apps.empresas.models import Empresa
from apps.curso.models import Curso
from apps.conferencia3.models import Conferencia3
from django.db.models import Sum


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
