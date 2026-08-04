from django.core.management import call_command
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.parcerias.models import Parcerias
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


class DemoCicloCompletoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("preparar_demo_ciclo_completo", verbosity=0)

    def test_cria_tres_prefeituras_e_tres_oscs(self):
        self.assertEqual(
            Empresa.objects.filter(nome__contains="Prefeitura Municipal").count(),
            3,
        )
        self.assertEqual(
            Parcerias.objects.filter(nomeOSC__contains="Demonstração").count(),
            3,
        )

    def test_cria_tres_termos_e_tres_prestacoes(self):
        self.assertEqual(Termos.objects.filter(numtermo__in=["001/2026", "002/2026", "003/2026"]).count(), 3)
        self.assertEqual(Prestacao.objects.filter(numtermo__in=["001/2026", "002/2026", "003/2026"]).count(), 3)

    def test_cria_33_lancamentos_por_osc(self):
        for empresa in Empresa.objects.filter(nome__contains="Prefeitura Municipal"):
            self.assertEqual(Lancamento.objects.filter(empresa=empresa).count(), 33)

    def test_comando_e_idempotente(self):
        call_command("preparar_demo_ciclo_completo", verbosity=0)
        self.assertEqual(
            Lancamento.objects.filter(
                empresa__nome__contains="Prefeitura Municipal"
            ).count(),
            99,
        )
