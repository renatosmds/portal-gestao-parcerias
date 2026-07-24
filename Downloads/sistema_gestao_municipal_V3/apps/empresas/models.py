from django.db import models  # ok
from django.urls import reverse
from django.db.models import Q
from django.db.models import Sum

#from apps.funcionarios.models import Funcionario
from apps.receitas.models import Receitas
from apps.curso.models import Curso

#from apps.registro_hora_extra.models import RegistroHoraExtra
from apps.conferencia3.models import Conferencia3
# from apps.auditorias.models import Auditorias


class Empresa(models.Model):  # ok
    class Meta:
        ordering = ["nome"]

    nome = models.CharField(max_length=100, help_text='Nome da empresa')  # ok

    receitas = models.ForeignKey(Receitas, on_delete=models.PROTECT, null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, null=True, blank=True)
    termos = models.ForeignKey(
        "termos.Termos",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="empresas_legadas",
        related_query_name="empresa_legada",
        verbose_name="Termo legado",
    )
    prestacao = models.ForeignKey(
        "prestacao.Prestacao",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="empresas_legadas",
        related_query_name="empresa_legada",
        verbose_name="Prestação legada",
    )
    conferencia3 = models.ForeignKey(Conferencia3, on_delete=models.PROTECT, null=True, blank=True)
    parcerias = models.ForeignKey(
        "parcerias.Parcerias",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="empresas_legadas",
        related_query_name="empresa_legada",
        verbose_name="Parceria legada",
    )


    # CARD EMPREGADOS #
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

    # CARD HORA-EXTRA #
    #@property
    #def total_hora_extra(self):
    #    return self.RegistroHoraExtra.objects.all().count()

    # CARD EXECUÇÃO #
    @property
    def totalOrdens(self):
        #return self.bpm.objects.all().count()
        return Conferencia3.objects.all().count()

    @property
    def ordensValor(self):
        return Conferencia3.objects.all().aggregate(Sum('valor'))['valor__sum']
        #return self.Conferencia3_set.all().aggregate(Sum('valor'))['valor__sum'] or 0
        #return self.bpm.objects.filter().aggregate(sum('valor'))

    @property
    def ordensConferir(self):
        return Conferencia3.objects.filter(conferido=False, notificado=False, aprovado=False).count()

    @property
    def valorTotalExecucao(self):
        return Conferencia3.objects.all().aggregate(Sum('valorTotalExecucao'))['repasse__sum']

    # CARD FINANCEIRO #
    # @property
    # def totalReceitas(self):
    #    return self.receitas.objects.all().count()










    @property
    def saldoRepasse(self):
        return Receitas.objects.all().aggregate(Sum('repasse'))['repasse__sum']

    @property
    def saldoDepositoOsc(self):
        return Receitas.objects.all().aggregate(Sum('depositoOsc'))['depositoOsc__sum']

    @property
    def saldoRendimento(self):
            return Receitas.objects.all().aggregate(Sum('rendimento'))['rendimento__sum']

    @property
    def saldoCreditoAutorizado(self):
        return Receitas.objects.all().aggregate(Sum('creditoAutorizado'))['creditoAutorizado__sum']

    @property
    def saldoResgateAutomatico(self):
        return Receitas.objects.all().aggregate(Sum('resgateAutomatico'))['resgateAutomatico__sum']

    @property
    def saldoEstorno(self):
        return Receitas.objects.all().aggregate(Sum('estorno'))['estorno__sum']

    @property
    def receitaTotal(self):
        return Receitas.objects.all().aggregate(Sum('repasse'))['repasse__sum'] + \
               Receitas.objects.all().aggregate(Sum('depositoOsc'))['depositoOsc__sum'] + \
               Receitas.objects.all().aggregate(Sum('rendimento'))['rendimento__sum'] + \
               Receitas.objects.all().aggregate(Sum('creditoAutorizado'))['creditoAutorizado__sum'] + \
               Receitas.objects.all().aggregate(Sum('estorno'))['estorno__sum']\

    @property
    def saldoAplicacao(self):
        return Receitas.objects.all().aggregate(Sum('aplicacao'))['aplicacao__sum']

    @property
    def saldoDebitoAutorizado(self):
        return Receitas.objects.all().aggregate(Sum('debitoAutorizado'))['debitoAutorizado__sum']

    @property
    def saldoDespesaBancaria(self):
        return Receitas.objects.all().aggregate(Sum('despesaBancaria'))['despesaBancaria__sum']

    @property
    def saldoImpostoRenda(self):
        return Receitas.objects.all().aggregate(Sum('impostoRenda'))['impostoRenda__sum']

    @property
    def saldoIof(self):
        return Receitas.objects.all().aggregate(Sum('iof'))['iof__sum']

    # @property
    # def saldoDespesas(self):
    #     return Conferencia3.objects.all().aggregate(Sum('valor'))['valor__sum']

    @property
    def despesaTotal(self):
        return Receitas.objects.all().aggregate(Sum('debitoAutorizado'))['debitoAutorizado__sum'] + \
               Receitas.objects.all().aggregate(Sum('despesaBancaria'))['despesaBancaria__sum'] + \
               Receitas.objects.all().aggregate(Sum('impostoRenda'))['impostoRenda__sum'] + \
               Receitas.objects.all().aggregate(Sum('iof'))['iof__sum'] + \
               Conferencia3.objects.all().aggregate(Sum('valor'))['valor__sum']\

    @property
    def saldoContaAplicacao(self):
        return Receitas.objects.all().aggregate(Sum('aplicacao'))['aplicacao__sum'] - \
               Receitas.objects.all().aggregate(Sum('resgateAutomatico'))['resgateAutomatico__sum']

    @property
    def saldoFinanceiro(self):
        return Receitas.objects.all().aggregate(Sum('repasse'))['repasse__sum'] + \
               Receitas.objects.all().aggregate(Sum('depositoOsc'))['depositoOsc__sum'] + \
               Receitas.objects.all().aggregate(Sum('rendimento'))['rendimento__sum'] + \
               Receitas.objects.all().aggregate(Sum('creditoAutorizado'))['creditoAutorizado__sum'] + \
               Receitas.objects.all().aggregate(Sum('resgateAutomatico'))['resgateAutomatico__sum'] + \
               Receitas.objects.all().aggregate(Sum('estorno'))['estorno__sum'] - \
               Receitas.objects.all().aggregate(Sum('aplicacao'))['aplicacao__sum'] - \
               Receitas.objects.all().aggregate(Sum('debitoAutorizado'))['debitoAutorizado__sum'] - \
               Receitas.objects.all().aggregate(Sum('despesaBancaria'))['despesaBancaria__sum'] - \
               Receitas.objects.all().aggregate(Sum('impostoRenda'))['impostoRenda__sum'] - \
               Receitas.objects.all().aggregate(Sum('iof'))['iof__sum'] - \
               Conferencia3.objects.all().aggregate(Sum('valor'))['valor__sum']\



    # CARD TERMOS #
    @property
    def valorglobaltotal(self):
        return Termos.objects.all().aggregate(Sum('valorglobal'))['valorglobal__sum']

    @property
    def valorRepasseTotal(self):
        return Termos.objects.all().aggregate(Sum('valorrepasse'))['valorrepasse__sum']

    @property
    def valorSaldoTotal(self):
        return Termos.objects.all().aggregate(Sum('valorsaldo'))['valorsaldo__sum']

    # CARD AUDITORIAS #
    @property
    def auditoriasQtd(self):
        return Parcerias.objects.all().count()
    @property
    def auditoriasAbertas(self):
        #return Parcerias.objects.all().count()
        return Parcerias.objects.filter(concluido=True).count()

    def __str__(self):
        return self.nome or f"Empresa #{self.pk}"

    @property
    def get_absolute_url(self):
        return reverse('home')
