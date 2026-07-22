# coding=utf-8
from django.db.models import Q
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# from apps.departamentos.models import Departamento
# from apps.empresas.models import Empresa
from apps.termos.models import Termos
from apps.fornecedores.models import Fornecedores
from django.db.models import Sum


def get_absolute_url():
    return reverse('list_parcerias')


class Parcerias(models.Model):
    objects = None

    class Meta:
        ordering = ["numtermo"]

    numtermo = models.CharField(max_length=8, null=True, blank=True, verbose_name='Parceria')
    nomeOSC = models.CharField(max_length=30, null=True, blank=True, verbose_name='OSC')
    fileTC = models.FileField(upload_to='parcerias_photos', null=True, blank=True,
                              verbose_name='TC')
    numRA = models.CharField(max_length=12, null=True, blank=True, verbose_name='RA')
    numOficioRA = models.CharField(max_length=30, null=True, blank=True, verbose_name='Ofício - RA')
    fileRA = models.FileField(upload_to='parcerias_photos', null=True, blank=True,
                              verbose_name='Relatório Auditoria (RA)')
    fileOficioRA = models.FileField(upload_to='parcerias_photos', null=True, blank=True,  verbose_name='Ofício RA')
    dtRaSMDS = models.DateField(null=True, blank=True, verbose_name='Entrada RA')
    respRA = models.CharField(max_length=3, null=True, blank=True, verbose_name='Resposta RA')
    numRE = models.CharField(max_length=12, null=True, blank=True, verbose_name='RE')
    numOficioRE = models.CharField(max_length=30, null=True, blank=True, verbose_name='Ofício - RE')
    fileRE = models.FileField(upload_to='parcerias_photos', null=True, blank=True,
                              verbose_name='Relatório Efetividade (RE)')
    fileOficioRE = models.FileField(upload_to='parcerias_photos', null=True, blank=True,  verbose_name='Ofício RE')
    dtReSMDS = models.DateField(null=True, blank=True, verbose_name='Entrada RE')
    respRE = models.CharField(max_length=3, null=True, blank=True, verbose_name='Resposta RE')
    fileRRE = models.FileField(upload_to='parcerias_photos', null=True, blank=True,  verbose_name='Resposta RE')
    prazoFinal = models.CharField(max_length=12, null=True, blank=True, verbose_name='Prazo Final')
    status = models.TextField(null=True, blank=True, verbose_name='Status')
    prazoDecorrido = models.CharField(max_length=8, null=True, blank=True, verbose_name='Prazo Decorrido')
    prazoRestante = models.CharField(max_length=8, null=True, blank=True, verbose_name='Prazo Restante')
    historico = models.TextField(null=True, blank=True, verbose_name='Histórico ')
    concluido = models.BooleanField(default=False, verbose_name='Concluído')
    photo = models.ImageField(upload_to='parcerias_photos', null=True, blank=True)

    user = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True)
    # departamento = models.ManyToManyField(Departamento)
    #empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, null=True, blank=True)
    numtermo = models.ForeignKey(Termos, on_delete=models.PROTECT, null=True, blank=True)
    credor = models.ForeignKey(Fornecedores, on_delete=models.PROTECT, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parcerias_set = None

    def __str__(self):
        return str(self.numtermo)
