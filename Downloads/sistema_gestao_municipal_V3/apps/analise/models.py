from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from apps.departamentos.models import Departamento
from apps.empresas.models import Empresa
from apps.termos.models import Termos
from django.db.models import Sum


def get_absolute_url():
    return reverse('list_analise')


class Analise(models.Model):
    objects = None
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    numtermo = models.CharField(max_length=50, verbose_name='Número Termo')
    nomeOSC = models.CharField(max_length=30, verbose_name='Nome OSC')
    numRA = models.CharField(max_length=12, verbose_name='Nº Relatório Auditoria (RA)')
    item = models.CharField(max_length=12, verbose_name='Item')
    inconformidade = models.TextField(verbose_name='Inconformidade')
    recomendacoes = models.TextField(verbose_name='Recomendações')
    posicaoSecretaria = models.TextField(verbose_name='Posição SMDS')
    status = models.CharField(max_length=50, verbose_name='Status')

    # user = models.OneToOneField(User, on_delete=models.PROTECT)
    # departamento = models.ManyToManyField(Departamento)
    # empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, null=True, blank=True)
    numtermo = models.ForeignKey(Termos, on_delete=models.PROTECT, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analise_set = None

    @property
    def analise(self):
        total = self.analise_set.filter(utilizada=False).aggregate(
            Sum('valor'))['valor__sum']
        return total or 0

    def __str__(self):
        return self.numParceria

# -- DROP TABLE public.colaboradores2_colaboradores2;

# CREATE TABLE public.colaboradores2_colaboradores2
# (
#  id integer NOT NULL DEFAULT nextval('colaboradores2_colaboradores1_id_seq'::regclass),
#  photo character varying(100),
#  nome character varying(100) NOT NULL,
#  sobrenome character varying(100) NOT NULL,
#  cargo character varying(100) NOT NULL,
#  "salarioBase" numeric(7,2) NOT NULL,
#  endereco character varying(100) NOT NULL,
#  bairro character varying(100) NOT NULL,
#  cep character varying(100) NOT NULL,
#  cidade character varying(100) NOT NULL,
#  estado character varying(100) NOT NULL,
#  email character varying(100) NOT NULL,
#  "dataNascimento" character varying(10) NOT NULL,
#  idade integer NOT NULL,
#  competencias text NOT NULL,
#  habilidades text NOT NULL,
#  atitudes text NOT NULL,
#  curriculo character varying(100),
#  CONSTRAINT colaboradores2_colaboradores1_pkey PRIMARY KEY (id)
# )
# WITH (
#  OIDS=FALSE
# );
# ALTER TABLE public.colaboradores2_colaboradores2
#  OWNER TO eqblxpqnqgqust;
