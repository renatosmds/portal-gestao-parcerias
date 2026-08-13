import os

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.analise.models import Analise
from apps.conciliacao.models import Conciliacao, Movimentacao, VinculoConciliacao
from apps.diligencias.models import Diligencia
from apps.documentos.models import Documento
from apps.departamentos.models import Departamento
from apps.empresas.models import Empresa
from apps.fornecedores.models import Fornecedores
from apps.lancamentos.models import Lancamento
from apps.metas.models import MetaExecucao
from apps.parcerias.models import Parcerias
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos
from apps.transparencia.models import PublicacaoDocumento, PublicacaoParceria


class Command(BaseCommand):
    help = (
        "Reseta exclusivamente os dados operacionais do ambiente demo "
        "e recria os cenarios demonstrativos padrao."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        if os.getenv("PGP_DEMO_RESET_ALLOWED") != "1":
            raise CommandError(
                "Reset bloqueado. Defina PGP_DEMO_RESET_ALLOWED=1 "
                "somente no ambiente demonstrativo."
            )

        self.stdout.write("=== RESET CONTROLADO DA BASE DEMO ===")

        # Ordem proposital: primeiro objetos dependentes,
        # depois objetos principais.

        PublicacaoDocumento.objects.all().delete()
        PublicacaoParceria.objects.all().delete()

        VinculoConciliacao.objects.all().delete()
        Movimentacao.objects.all().delete()

        Diligencia.objects.all().delete()
        Documento.objects.all().delete()
        Analise.objects.all().delete()
        MetaExecucao.objects.all().delete()
        Lancamento.objects.all().delete()

        Conciliacao.objects.all().delete()
        Empresa.objects.update(parcerias=None)
        Parcerias.objects.all().delete()

        Fornecedores.objects.all().delete()

        # Remove refer?ncias PROTECT mantidas por Empresa.
        Empresa.objects.update(
            prestacao=None,
            termos=None,
        )

        Prestacao.objects.all().delete()
        Termos.objects.all().delete()

        # Departamento.empresa usa PROTECT e nao aceita NULL.
        Departamento.objects.all().delete()

        Empresa.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                "Dados operacionais da demo removidos."
            )
        )

        call_command("preparar_demo_ciclo_completo")

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Base demonstrativa recriada com sucesso."
            )
        )
