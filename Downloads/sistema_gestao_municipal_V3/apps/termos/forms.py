from django.forms import ModelForm
from .models import Termos


class TermosForm(ModelForm):
    class Meta:
        model = Termos
        fields = ['nomeosc', 'numtermo', 'numpa', 'vigencia', 'assinatura', 'valorglobal', 'valorrepasse',
                  'valorsaldo', 'parcelasAbertas', 'numdispensa', 'nomemunicipio', 'nomeintermediario', 'nomesecretario',
                  'nomerepresentante', 'tipo', 'termo', 'apelido', 'parceria', 'objeto', 'relatoriosDeSinteses',
                  'inicioVigencia', 'terminoVigencia', 'analista', 'status', 'saldoDashboard',
                  'saldoContaSinteseDespesas', 'rendimento', 'saldoContaSinteseMovFinanceira', 'valorDevolvido',
                  'saldoFinal', 'totalDeLacamentos', 'lacamentosRegulares', 'lacamentosIrregulares',
                  'lacamentosGlosados', 'lacamentosNaoEnviados', 'naoanalisados', 'total', 'extratosBancarios',
                  'pendenciasOfx', 'valoresGlosados', 'glosasRestituidas', 'saldoGlosas', 'observacoes'
                  ]
