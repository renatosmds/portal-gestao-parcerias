# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# from apps.departamentos.models import Departamento
# from apps.empresas.models import Empresa
from django.db.models import Sum, Avg, Max, Min, Count, FloatField, F
from apps.termos.models import Termos


def get_absolute_url():
    return reverse('list_receitas')


class Receitas(models.Model):
    objects = None

    class Meta:
        ordering = ["id"]

    PARCELA_CHOICES = (u'1', u'1'), (u'2', u'2'), (u'3', u'3'), (u'4', u'4'), (u'5', u'5'), (u'6', u'6'), (u'7', u'7'),\
                      (u'8', u'8'), (u'9', u'9'), (u'10', u'10'), (u'11', u'11'), (u'12', u'12')

    ENTE_CHOICES = (u'municipal', u'Municipal'), (u'estadual', u'Estadual'), (u'federal', u'Federal')

    osc = models.CharField(max_length=30, verbose_name='OSC')
    numtermo = models.CharField(max_length=50, verbose_name='Número Termo')
    parcela = models.CharField(max_length=2, choices=PARCELA_CHOICES, verbose_name='Parcela')
    ente = models.CharField(max_length=10, choices=ENTE_CHOICES, verbose_name='Ente')
    fonte = models.CharField(max_length=5, verbose_name='Fonte')
    conta = models.CharField(max_length=10, verbose_name='Conta')

    data = models.DateField(verbose_name='Data')
    saldoAnterior = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                        verbose_name='Saldo Anterior')
    repasse = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='Repasse - NAP')
    depositoOsc = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                      verbose_name='Depósito OSC')
    rendimento = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                     verbose_name='Rendimento Aplicação')
    creditoAutorizado = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                            verbose_name='Crédito Autorizado')
    resgateAutomatico = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                            verbose_name='Resgate Automático')
    estorno = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='Estorno')
    totalReceitas = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                        verbose_name='Total Receitas')
    aplicacao = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                    verbose_name='Aplicação Financeira')
    debitoAutorizado = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                           verbose_name='Débito Autorizado')
    despesaBancaria = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                          verbose_name='Despesa Bancária')
    impostoRenda = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='IR')
    iof = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='IOF')
    despesas = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name='Pagamentos')
    totalDespesas = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                        verbose_name='Total Despesas')
    saldoBancario = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                        verbose_name='Saldo Final')
    fileNap = models.FileField(upload_to='receitas_fotos', blank=True, null=True, verbose_name='NAP')
    fileDepositoTicket = models.FileField(upload_to='receitas_fotos', blank=True, null=True,
                                          verbose_name='Comprovante Depósito Tickets')
    fileDepositoOsc = models.FileField(upload_to='receitas_fotos', blank=True, null=True,
                                       verbose_name='Comprovante Depósito OSC')
    fileAplicacao = models.FileField(upload_to='receitas_fotos', blank=True, null=True,
                                     verbose_name='Comprovante de Aplicação Financeira')
    fileContrapartida = models.FileField(upload_to='receitas_fotos', blank=True, null=True,
                                         verbose_name='Comprovante de Contrapartida')
    fileEstorno = models.FileField(upload_to='receitas_fotos', blank=True, null=True,
                                   verbose_name='Comprovante de Estorno')
    conferido = models.BooleanField(verbose_name='Conferido')
    notificado = models.BooleanField(verbose_name='Notificado')
    aprovado = models.BooleanField(verbose_name='Aprovado')
    notificacao = models.CharField(max_length=500, null=True, blank=True, verbose_name='Notificações')

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    # departamento = models.ManyToManyField(Departamento)
    # empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, null=True, blank=True)
    numtermo = models.ForeignKey(Termos, on_delete=models.PROTECT, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receitas_set = None

    def __str__(self):
        return self.parcela
