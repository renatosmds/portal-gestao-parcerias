# coding=utf-8
from django.conf import settings
from django.db import models
# from django.contrib.auth.models import User
from django.urls import reverse
# from apps.departamentos.models import Departamento
# from apps.empresas.models import Empresa
# from apps.termos.models import Termos
from django.db.models import Sum


class Prestacao(models.Model):

    class SituacaoWorkflow(models.TextChoices):
        ELABORACAO = "elaboracao", "Em elaboração"
        ENVIADA = "enviada", "Enviada pela OSC"
        RECEBIDA = "recebida", "Recebida pelo órgão"
        EM_ANALISE = "em_analise", "Em análise"
        DILIGENCIA = "diligencia", "Em diligência"
        CORRIGIDA = "corrigida", "Corrigida pela OSC"
        APROVADA = "aprovada", "Aprovada"
        APROVADA_RESSALVAS = "aprovada_ressalvas", "Aprovada com ressalvas"
        REPROVADA = "reprovada", "Reprovada"
        ENCERRADA = "encerrada", "Encerrada"
    class Meta:
        ordering = ["numtermo", "tipoTermo"]
        verbose_name = "Prestação de contas"
        verbose_name_plural = "Prestações de contas"

    TIPOTERMO_CHOICES = (u'TF', u'TF'), (u'TC', u'TC'), (u'CONVÊNIO', u'Convênio'), (u'ASSOCIAÇÃO', u'Associação')
    TIPO_CHOICES = (u'cnpj', u'CNPJ'), (u'cpf', u'CPF')
    QTDPARCELAS_CHOICES = (u'1', u'1'), (u'2', u'2'), (u'3', u'3'), (u'4', u'4'), (u'5', u'5'), (u'6', u'6'),\
                          (u'7', u'7'), (u'8', u'8'), (u'9', u'9'), (u'10', u'10'), (u'11', u'11'), (u'12', u'12'),\
                          (u'13', u'13'), (u'14', u'14'), (u'15', u'15'), (u'16', u'16'), (u'17', u'17'),\
                          (u'18', u'18'), (u'19', u'19'), (u'20', u'20'), (u'21', u'21'), (u'22', u'22'),\
                          (u'23', u'23'), (u'24', u'24')
    MES_CHOICES = (u'Janeiro', u'JANEIRO'), (u'fevereiro', u'FEVEREIRO'), (u'março', u'MARÇO'), (u'abril', u'ABRIL'),\
                  (u'maio', u'MAIO'), (u'junho', u'JUNHO'), (u'julho', u'JULHO'), (u'agosto', u'AGOSTO'), \
                  (u'setembro', u'SETEMBRO'), (u'outubro', u'OUTUBRO'), (u'novembro', u'NOVEMBRO'), \
                  (u'dezembro', u'DEZEMBRO')
    ANO_CHOICES = (u'2000', u'2000'), (u'2001', u'2001'), (u'2002', u'2002'), (u'2003', u'2003'), (u'2004', u'2004'), \
                  (u'2005', u'2005'), (u'2006', u'2006'), (u'2007', u'2007'), (u'2008', u'2008'), (u'2009', u'2009'), \
                  (u'2010', u'2010'), (u'2011', u'2011'), (u'2012', u'2012'), (u'2013', u'2013'), (u'2014', u'2014'),\
                  (u'2015', u'2015'), (u'2016', u'2016'), (u'2017', u'2017'), (u'2018', u'2018'), (u'2019', u'2019'), \
                  (u'2020', u'2020'), (u'2021', u'2021'), (u'2022', u'2022'), (u'2023', u'2023'), (u'2024', u'2024'), \
                  (u'2025', u'2025'), (u'2026', u'2026'), (u'2027', u'2027'), (u'2028', u'2028'), (u'2029', u'2029'), \
                  (u'2030', u'2030'), (u'2031', u'2031'), (u'2032', u'2032'), (u'2033', u'2033'), (u'2034', u'2034'), \
                  (u'2035', u'2035')

    tipoTermo = models.CharField(max_length=15, choices=TIPOTERMO_CHOICES, blank=True, null=True,
                                 verbose_name='Tipo de Termo')
    numtermo = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número do Termo')
    termoAditivo = models.CharField(max_length=2, blank=True, null=True, verbose_name='Termo Aditivo')
    credor = models.CharField(max_length=50, blank=True, null=True, verbose_name='Credor')
    numCredor = models.IntegerField(blank=True, null=True, verbose_name='Número do Credor')
    tipo = models.CharField(max_length=4, choices=TIPO_CHOICES, verbose_name='Tipo')
    CpfCnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name='CPF/CNPJ')
    oficioCcoaf = models.CharField(max_length=10, blank=True, null=True, verbose_name='Ofício CCOAF')
    sco = models.CharField(max_length=10, blank=True, null=True, verbose_name='S.C.O.')
    agCredito = models.CharField(max_length=10, null=True, blank=True, verbose_name='Nº Ag. Crédito')
    ccCredito = models.CharField(max_length=10, blank=True, null=True, verbose_name='Nº C.C. Crédito')
    uo = models.CharField(max_length=4, blank=True, null=True, verbose_name='Unidade Orçamentária - UO')
    funcao = models.CharField(max_length=2, blank=True, null=True, verbose_name='Função')
    subfuncao = models.CharField(max_length=3, blank=True, null=True, verbose_name='Sub Função')
    programa = models.CharField(max_length=4, blank=True, null=True, verbose_name='Programa')
    projeto = models.CharField(max_length=4, blank=True, null=True, verbose_name='Projeto / Atividade')
    natureza = models.CharField(max_length=20, blank=True, null=True, verbose_name='Natureza')
    fonte = models.CharField(max_length=20, blank=True, null=True, verbose_name='Fonte')
    cod_reduz = models.CharField(max_length=50, blank=True, null=True, verbose_name='Nome do Gestor(a)')
    bancoCredor = models.CharField(max_length=3, blank=True, null=True, verbose_name='Banco Credor')
    agCredor = models.CharField(max_length=20, blank=True, null=True, verbose_name='Agência Credor')
    ccCredor = models.CharField(max_length=20, blank=True, null=True, verbose_name='Conta Corrente Credor')
    gestora = models.CharField(max_length=50, blank=True, null=True, verbose_name='Reduzida')
    matricula = models.CharField(max_length=10, blank=True, null=True, verbose_name='Matrícula do Gestor(a)')
    contato = models.CharField(max_length=20, blank=True, null=True, verbose_name='Contato do Gestor(a)')
    valorContrato = models.FloatField(max_length=20, blank=True, null=True, verbose_name='Valor do Contrato')
    qtdParcelas = models.CharField(max_length=2, choices=QTDPARCELAS_CHOICES, blank=True, null=True,
                                   verbose_name='Qtd de Parcelas')
    mesParcela1 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True, verbose_name='PARCELA 1')
    anoParcela1 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela1 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela1 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela1 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela1 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela2 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True, verbose_name='PARCELA 2')
    anoParcela2 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela2 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela2 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela2 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela2 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela3 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True, verbose_name='PARCELA 3')
    anoParcela3 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela3 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela3 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela3 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela3 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela4 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True, verbose_name='PARCELA 4')
    anoParcela4 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela4 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela4 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela4 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela4 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela5 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True, verbose_name='PARCELA 5')
    anoParcela5 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela5 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela5 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela5 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela5 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela6 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True, verbose_name='PARCELA 6')
    anoParcela6 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela6 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela6 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela6 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela6 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela7 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True, verbose_name='PARCELA 7')
    anoParcela7 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela7 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela7 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela7 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela7 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela8 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True, verbose_name='PARCELA 8')
    anoParcela8 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela8 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela8 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela8 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela8 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela9 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True, verbose_name='PARCELA 9')
    anoParcela9 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela9 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela9 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela9 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela9 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela10 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True,
                                    verbose_name='PARCELA 10')
    anoParcela10 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela10 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela10 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela10 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela10 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela11 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True,
                                    verbose_name='PARCELA 11')
    anoParcela11 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela11 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela11 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela11 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela11 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    mesParcela12 = models.CharField(max_length=10, choices=MES_CHOICES, null=True, blank=True,
                                    verbose_name='PARCELA 12')
    anoParcela12 = models.CharField(max_length=4, choices=ANO_CHOICES, null=True, blank=True, verbose_name='Ano')
    valorParcela12 = models.FloatField(max_length=15, null=True, blank=True, verbose_name='Valor')
    empenhoParcela12 = models.IntegerField(null=True, blank=True, verbose_name='Nº Empenho')
    napParcela12 = models.IntegerField(null=True, blank=True, verbose_name='Nº NAP')
    dataNapParcela12 = models.DateField(null=True, blank=True, verbose_name='Data Pagto NAP')
    concluida = models.BooleanField(default=False)

    situacao_workflow = models.CharField(
        max_length=24, choices=SituacaoWorkflow.choices,
        default=SituacaoWorkflow.ELABORACAO, verbose_name="Situação do fluxo"
    )
    analista_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="prestacoes_atribuidas", verbose_name="Analista responsável"
    )
    enviada_em = models.DateTimeField(null=True, blank=True)
    recebida_em = models.DateTimeField(null=True, blank=True)

    imagem = models.ImageField(blank=True, null=True)
    de_ferias = models.BooleanField(default=False)

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="prestacoes_vinculadas",
        related_query_name="prestacao_vinculada",
        verbose_name="Empresa",
    )

    def get_absolute_url(self):
        return reverse("detail_prestacao", kwargs={"pk": self.pk})

    def __str__(self):
        return (
            self.numtermo
            or self.credor
            or self.CpfCnpj
            or f"Prestação #{self.pk}"
        )


class HistoricoPrestacao(models.Model):
    prestacao = models.ForeignKey(Prestacao, on_delete=models.CASCADE, related_name="historico_workflow")
    situacao_anterior = models.CharField(max_length=24, blank=True)
    nova_situacao = models.CharField(max_length=24, choices=Prestacao.SituacaoWorkflow.choices)
    observacao = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Histórico da prestação"
        verbose_name_plural = "Históricos das prestações"

    def __str__(self):
        return f"{self.prestacao} — {self.get_nova_situacao_display()}"
