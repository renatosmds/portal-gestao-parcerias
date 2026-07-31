# coding=utf-8
from django.db.models import Q, DecimalField, CharField
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# from apps.departamentos.models import Departamento
#from apps.empresas.models import Empresa
from apps.fornecedores.models import Fornecedores
from apps.termos.models import Termos
from django.db.models import Sum


def get_absolute_url():
    return reverse('list_conferencia3')


class Conferencia3(models.Model):
    objects = None

    class Meta:
        ordering = ["ordem"]

    PARCELAS_CHOICES = (u'1', u'1'), (u'2', u'2'), (u'3', u'3'), (u'4', u'4'), (u'5', u'5'), (u'6', u'6'), \
                       (u'7', u'7'), (u'8', u'8'), (u'9', u'9'), (u'10', u'10'), (u'11', u'11'), (u'12', u'12'), \
                       (u'13', u'13'), (u'14', u'14'), (u'15', u'15'), (u'16', u'16'), (u'17', u'17'), (u'18', u'18'), \
                       (u'19', u'19'), (u'20', u'20'), (u'21', u'21'), (u'22', u'22'), (u'23', u'23'), (u'24', u'24')

    RUBRICANIVEL1_CHOICES = (u'1 - pessoal e encargos sociais', u'1 - Pessoal e Encargos Sociais'), \
                            (u'2 - gêneros alimentícios', u'2 - Gêneros Alimentícios'), \
                            (u'3 - material consumo', u'3 - Material Consumo'), \
                            (u'4 - custos indiretos', u'4 - Custos Indiretos')

    RUBRICANIVEL2_CHOICES = (
        (u'1.1 - pagamento de remunueração', u'1.1 - Pagamento de Remuneração'),
        (u'1.2 - pagamento de encargos sociais, tributos e benefícios',
         u'1.2 - Pagamento de Encargos Sociais, Tributos e Benefícios'),
        (u'2.1 - gêneros de alimentação', u'2.1 - Gêneros de Alimentação'),
        (u'3.1 - epi´s', u'3.1 - Epi´s'),
        (u'3.2 - material de limpeza', u'3.2 - Material de Limpeza'),
        (u'3.3 - material descartável', u'3.3 - Material Descartáve'),
        (u'3.4 - material de copa e cozinha', u'3.4 - Material de Copa e Cozinha'),
        (u'3.5 - material de higiene dos gêneros alimentícios', u'3.5 - Material de Higiene dos Gêneros Alimentícios'),
        (u'3.6 - material de expediente', u'3.6 - Material de Expediente'),
        (u'4.1 - serviços de departamento pessoal e medicina do trabalho',
         u'4.1 - Serviços de Departamento Pessoal e Medicina do Trabalho'),
        (u'4.2 - serviços de telefonia', u'4.2 - Serviços de Telefonia'),
        (u'4.3 - serviços gráficos e comunicação', u'4.3 - Serviços Gráficos e Comunicação'),
        (u'4.4 - serviço de manutenção e conservação (imóveis)',
         u'4.4 - Serviço de Manutenção e Conservação (Imóveis)'),
        (u'4.5 - serviço de manutenção e conservação (máquinas e equipamentos)',
         u'4.5 - Serviço de Manutenção e Conservação (Máquinas e Equipamentos)'),
        (u'4.6 - locação de máquinas e equipamentos', u'4.6 - Locação de Máquinas e Equipamentos'),
        (u'4.7 - locação de imóveis', u'4.7 - Locação de Imóveis'),
        (u'4.8 - gás', u'4.8 - Gás'),
        (u'4.9 - energia elétrica', u'4.9 - Energia Elétrica'),
        (u'4.10 - despesa com pessoal indireto', u'4.10 - Despesa com Pessoal Indireto'),

    )

    RUBRICANIVEL3_CHOICES = (u'1.1.1 - 13º salário', u'1.1.1 - 13º Salário'), \
                            (u'1.1.2 - adicional de férias', u'1.1.2 - Adicional de Férias'), \
                            (u'1.1.3 - férias', u'1.1.3 - Férias'), \
                            (u'1.1.4 - aviso prévio indenizado', u'1.1.4 - Aviso Prévio Indenizado'), \
                            (u'1.2.1 - inss', u'1.2.1 - INSS'), (u'1.2.2 - fgts', u'1.2.2 - FGTS'), \
                            (u'1.2.3 - pis/pasep', u'1.2.3 - PIS/PASEP'), \
                            (u'1.2.4 - ausência remunerada', u'1.2.4 - Ausência Remunerada'), \
                            (u'1.2.5 - licenças', u'1.2.5 - Licenças'), \
                            (u'1.2.6 - vale transporte', u'1.2.6 - Vale Transporte'), \
                            (u'1.2.7 - outros benefícios', u'1.2.7 - Outros Benefícios'), \
                            (u'1.9.9 - outros - pessoal e encargos sociais',
                             u'1.9.9 - Outros - Pessoal e Encargos Sociais'), \
                            (u'2.9.9 - outros - gêneros alimentícios', u'2.9.9 - Outros Gêneros Alimentícios'), \
                            (u'3.9.9 - outros - material consumo', u'3.9.9 - Outros Material Consumo'), \
                            (u'4.9.9 - outros - custos indiretos', u'4.9.9 - Outros Custos Indiretos')

    TIPO_CHOICES = (u'cnpj', u'CNPJ'), (u'cpf', u'CPF')

    ESPECIE_CHOICES = (u'1ª parcela 13º salário', u'1ª Parcela 13º Salário'), \
                      (u'2ª parcela 13º salário', u'2ª Parcela 13º Salário'), (u'boleto', u'Boleto'), \
                      (u'danfe', u'DANFE'), (u'trct', u'Trct'), (u'fat. Locação', u'Fat. Locação'), \
                      (u'fatura', u'Fatura'), (u'férias', u'Férias'), (u'fgts', u'FGTS'), (u'gps', u'GPS'), \
                      (u'grrf', u'GRRF'), (u'guia darf', u'Guia Darf'), (u'guia fgts', u'Guia FGTS'), \
                      (u'guia gps', u'Guia GPS'), (u'guia issqn', u'Guia ISSQN'), (u'nf', u'NF'), (u'nfs-e', u'NFS-e'), \
                      (u'recibo', u'Recibo'), (u'recibo férias', u'Recibo Férias'), \
                      (u'recibo pagto', u'Recibo Pagto'), (u'reembolso de passivo', u'Reembolso de Passivo'), \
                      (u'tarifa bancária', u'Tarifa Bancária'), (u'trct', u'TRCT'), (u'trct dissídio', u'TRCT Dissídio')

    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    numtermo = models.CharField(max_length=50, verbose_name='Número Termo')
    parcela = models.CharField(max_length=50, choices=PARCELAS_CHOICES, verbose_name='Parcela')
    ordem = models.CharField(max_length=5, verbose_name='Ordem')
    rubricaNivel1 = models.CharField(max_length=100, choices=RUBRICANIVEL1_CHOICES, verbose_name='Rubrica Nível 1')
    rubricaNivel2 = models.CharField(max_length=100, choices=RUBRICANIVEL2_CHOICES, verbose_name='Rubrica Nível 2')
    rubricaNivel3 = models.CharField(max_length=100, choices=RUBRICANIVEL3_CHOICES, verbose_name='Rubrica Nível 3')
    outrobeneficio = models.CharField(db_column='outroBeneficio', max_length=100, verbose_name='Especificar Outro')
    credor: CharField = models.CharField(max_length=100, verbose_name='Credor')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name='Tipo')
    CpfCnpj = models.CharField(max_length=50, verbose_name='CPF/CNPJ')
    especie = models.CharField(max_length=50, choices=ESPECIE_CHOICES, verbose_name='Especie')
    numero = models.CharField(max_length=15, verbose_name='Numero')
    data = models.DateField(verbose_name='Data')
    comprovante = models.CharField(max_length=50, verbose_name='Comprovante')
    valor = models.DecimalField(max_digits=10, decimal_places=2,
                                              help_text='Separar centavos com . (ponto)',
                                              verbose_name='Valor')
    fileBoleto = models.FileField(upload_to='prestacao_photos', blank=True, null=True, verbose_name='Boleto')
    fileNF = models.FileField(upload_to='prestacao_photos', blank=True, null=True, verbose_name='Nota Fiscal')
    fileComprPag = models.FileField(upload_to='prestacao_photos', blank=True, null=True,
                                    verbose_name='Comprovante de Pagamento')
    fileOrcamentos = models.FileField(upload_to='prestacao_photos', blank=True, null=True, verbose_name='Orçamentos')
    photo = models.ImageField(upload_to='prestacao_photos', null=True, blank=True)
    conferido = models.BooleanField(verbose_name='Conferido')
    notificado = models.BooleanField(verbose_name='Notificado')
    aprovado = models.BooleanField(verbose_name='Aprovado')
    notificacao = models.TextField(verbose_name='Notificações')

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    # departamento = models.ManyToManyField(Departamento)
    #empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, null=True, blank=True)
    numtermo = models.ForeignKey(Termos, on_delete=models.PROTECT, null=True, blank=True)
    credor = models.ForeignKey(Fornecedores, on_delete=models.PROTECT, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conferencia3_set = None

    def __int__(self):
        return self.valor
