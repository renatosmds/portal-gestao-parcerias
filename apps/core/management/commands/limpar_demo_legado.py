from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from apps.empresas.models import Empresa
from apps.metas.models import MetaExecucao
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


TERMOS_DEMO = ("001/2026", "002/2026", "003/2026")

EMPRESAS_ATUAIS = {
    "001/2026": "Prefeitura de Vale Sereno ? Demo",
    "002/2026": "Prefeitura de Nova Esperan?a ? Demo",
    "003/2026": "Prefeitura de Jardim das ?guas ? Demo",
}

METAS_ATUAIS = {
    "001/2026": {"M1.1", "M1.2", "M1.3"},
    "002/2026": {"M2.1", "M2.2", "M2.3"},
    "003/2026": {"M3.1", "M3.2", "M3.3"},
}


class Command(BaseCommand):
    help = (
        "Higieniza exclusivamente a base demonstrativa, preservando "
        "os tres cenarios Demo atuais."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("=== HIGIENIZACAO DEFINITIVA DA BASE DEMO ===")

        empresas_atuais = {}

        for termo_numero, nome_empresa in EMPRESAS_ATUAIS.items():
            empresa = Empresa.objects.filter(nome=nome_empresa).first()

            if not empresa:
                self.stdout.write(
                    self.style.WARNING(
                        f"Cenario atual ainda nao existe: {nome_empresa}"
                    )
                )
                continue

            empresas_atuais[termo_numero] = empresa

        ids_empresas_atuais = {
            empresa.pk for empresa in empresas_atuais.values()
        }

        # Presta??es antigas dos tr?s termos demonstrativos.
        prestacoes_legadas = Prestacao.objects.filter(
            numtermo__in=TERMOS_DEMO
        ).exclude(
            empresa_id__in=ids_empresas_atuais
        )

        prestacoes_ids = list(
            prestacoes_legadas.values_list("pk", flat=True)
        )

        # Termos antigos dos tr?s cen?rios.
        termos_legados = Termos.objects.filter(
            numtermo__in=TERMOS_DEMO
        ).exclude(
            empresa_id__in=ids_empresas_atuais
        )

        termos_ids = list(
            termos_legados.values_list("pk", flat=True)
        )

        # Empresas antigas explicitamente demonstrativas/fict?cias.
        empresas_legadas = Empresa.objects.filter(
            Q(nome__icontains="Demonstra")
            | Q(nome__icontains="Ficticia")
            | Q(nome__icontains="Fict?cia")
        ).exclude(
            pk__in=ids_empresas_atuais
        )

        empresas_ids = list(
            empresas_legadas.values_list("pk", flat=True)
        )

        self.stdout.write(
            f"Prestacoes antigas: {len(prestacoes_ids)}"
        )
        self.stdout.write(
            f"Termos antigos: {len(termos_ids)}"
        )
        self.stdout.write(
            f"Empresas antigas: {len(empresas_ids)}"
        )

        # Remove refer?ncias PROTECT existentes em Empresa.
        if prestacoes_ids:
            Empresa.objects.filter(
                prestacao_id__in=prestacoes_ids
            ).update(prestacao=None)

        if termos_ids:
            Empresa.objects.filter(
                termos_id__in=termos_ids
            ).update(termos=None)

        # Remove primeiro os registros operacionais antigos.
        if prestacoes_ids:
            Prestacao.objects.filter(
                pk__in=prestacoes_ids
            ).delete()

        if termos_ids:
            Termos.objects.filter(
                pk__in=termos_ids
            ).delete()

        # Agora remove as empresas explicitamente legadas.
        if empresas_ids:
            Empresa.objects.filter(
                pk__in=empresas_ids
            ).delete()

        # Normaliza as metas dos tr?s cen?rios atuais.
        metas_removidas = 0

        for termo_numero, empresa in empresas_atuais.items():
            prestacao = Prestacao.objects.filter(
                numtermo=termo_numero,
                empresa=empresa,
            ).first()

            if not prestacao:
                continue

            codigos_validos = METAS_ATUAIS[termo_numero]

            extras = MetaExecucao.objects.filter(
                prestacao=prestacao
            ).exclude(
                codigo__in=codigos_validos
            )

            qtd = extras.count()

            if qtd:
                extras.delete()
                metas_removidas += qtd

        self.stdout.write(
            f"Metas excedentes removidas: {metas_removidas}"
        )

        self.stdout.write("")
        self.stdout.write("=== RESULTADO DA HIGIENIZACAO ===")
        self.stdout.write(
            f"Empresas: {Empresa.objects.count()}"
        )
        self.stdout.write(
            f"Termos: {Termos.objects.count()}"
        )
        self.stdout.write(
            f"Prestacoes: {Prestacao.objects.count()}"
        )
        self.stdout.write(
            f"Metas: {MetaExecucao.objects.count()}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Higienizacao definitiva da base demo concluida."
            )
        )
