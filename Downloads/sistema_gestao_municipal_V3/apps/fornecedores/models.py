# coding=utf-8
from django.db.models import Q
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# from apps.departamentos.models import Departamento
# from apps.empresas.models import Empresa
# from django.db.models import Sum


def get_absolute_url():
    return reverse('list_fornecedores')


class Fornecedores(models.Model):
    objects = None

    class Meta:
        ordering = ["credor"]

    TIPO_CHOICES = ((u'cnpj', u'CNPJ'), (u'cpf', u'CPF'))

    PESSOA_CHOICES = ((u'física', u'Física'), (u'jurídica', u'Jurídica'))

    credor = models.CharField(max_length=100, blank=True, null=True, help_text='Nome do Credor')
    pessoa = models.CharField(max_length=50, choices=PESSOA_CHOICES, blank=True, null=True, verbose_name='Pessoa')
    razao = models.CharField(max_length=100, blank=True, null=True, verbose_name='Razao Social')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, blank=True, null=True, verbose_name='CPF/CNPJ')
    numero = models.CharField(max_length=50, blank=True, null=True, verbose_name='Numero')
    fantasia = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nome Fantasia')
    endereco = models.CharField(max_length=100, blank=True, null=True, verbose_name='Endereço')
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bairro')
    cep = models.CharField(max_length=100, blank=True, null=True, verbose_name='CEP')
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cidade')
    estado = models.CharField(max_length=100, blank=True, null=True, verbose_name='Estado')
    email = models.CharField(max_length=100, blank=True, null=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=100, blank=True, null=True, verbose_name='Telefone')
    iestadual = models.CharField(max_length=100, blank=True, null=True, verbose_name='Inscrição Estadual')
    imunicipal = models.CharField(max_length=100, blank=True, null=True, verbose_name='Inscrição Municipal')

    user = models.OneToOneField(User, on_delete=models.PROTECT, blank=True, null=True, )
    # departamento = models.ManyToManyField(Departamento)
    # empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.funcionario_set = None

    @property
    def total_funcionarios(self):
        return self.funcionario_set.all().count()

    @property
    def total_funcionarios_ferias(self):
        return self.funcionario_set.filter(de_ferias=True).count()

    @property
    def total_funcionarios_doc_pendente(self):
        return self.funcionario_set.filter(Q(documento=None)).count()

    @property
    def total_funcionarios_doc_ok(self):
        return self.funcionario_set.filter(~Q(documento=None)).count()

    #    @property
    #    def fornecedores(self):
    #        total = self.fornecedores_set.filter(utilizada=False).aggregate(
    #            Sum('valor'))['valor__sum']
    #        return total or 0

    def __str__(self):
        return self.credor
