from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from apps.empresas.models import Empresa
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


MARCADOR_LEGADO = "Demonstra??o"


class Command(BaseCommand):
    help = (
        "Remove exclusivamente registros legados da base demonstrativa, "
        "preservando os cen?rios atuais identificados como Demo."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        empresas_legadas = Empresa.objects.filter(
            nome__icontains=MARCADOR_LEGADO
        )

        empresas_ids = list(
            empresas_legadas.values_list("pk", flat=True)
        )

        prestacoes_vinculadas_ids = list(
            empresas_legadas.exclude(prestacao_id__isnull=True)
            .values_list("prestacao_id", flat=True)
        )

        termos_vinculados_ids = list(
            empresas_legadas.exclude(termos_id__isnull=True)
            .values_list("termos_id", flat=True)
        )

        prestacoes_legadas = Prestacao.objects.filter(
            Q(pk__in=prestacoes_vinculadas_ids)
            | Q(empresa__in=empresas_legadas)
            | Q(credor__icontains=MARCADOR_LEGADO)
        ).distinct()

        termos_legados = Termos.objects.filter(
            Q(pk__in=termos_vinculados_ids)
            | Q(empresa__in=empresas_legadas)
        ).distinct()

        prestacoes_ids = list(
            prestacoes_legadas.values_list("pk", flat=True)
        )
        termos_ids = list(
            termos_legados.values_list("pk", flat=True)
        )

        self.stdout.write("=== HIGIENIZA??O DA BASE DEMO ===")
        self.stdout.write(
            f"Empresas legadas encontradas: {len(empresas_ids)}"
        )
        self.stdout.write(
            f"Presta??es legadas encontradas: {len(prestacoes_ids)}"
        )
        self.stdout.write(
            f"Termos legados encontrados: {len(termos_ids)}"
        )

        if not empresas_ids and not prestacoes_ids and not termos_ids:
            self.stdout.write(
                self.style.SUCCESS(
                    "Nenhum registro legado encontrado."
                )
            )
            return

        # Alguns registros de Empresa mant?m refer?ncias protegidas
        # para Presta??o e Termo. Esses v?nculos precisam ser removidos
        # antes da exclus?o dos registros legados.
        if prestacoes_ids:
            Empresa.objects.filter(
                prestacao_id__in=prestacoes_ids
            ).update(prestacao=None)

        if termos_ids:
            Empresa.objects.filter(
                termos_id__in=termos_ids
            ).update(termos=None)

        # A exclus?o da presta??o remove por cascata os registros
        # operacionais diretamente vinculados a ela.
        if prestacoes_ids:
            Prestacao.objects.filter(
                pk__in=prestacoes_ids
            ).delete()

        if termos_ids:
            Termos.objects.filter(
                pk__in=termos_ids
            ).delete()

        # Tenta remover as empresas legadas somente depois dos
        # respectivos termos e presta??es.
        empresas_restantes = Empresa.objects.filter(
            pk__in=empresas_ids
        )

        removidas = 0

        for empresa in empresas_restantes:
            try:
                empresa.delete()
                removidas += 1
            except Exception as exc:
                self.stdout.write(
                    self.style.WARNING(
                        f"Empresa legada ID {empresa.pk} n?o removida: {exc}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Higieniza??o dos registros legados conclu?da."
            )
        )
        self.stdout.write(
            f"Empresas removidas: {removidas}"
        )

        self.stdout.write("")
        self.stdout.write("=== BASE ATUAL ===")
        self.stdout.write(
            f"Empresas com marcador legado: "
            f"{Empresa.objects.filter(nome__icontains=MARCADOR_LEGADO).count()}"
        )
        self.stdout.write(
            f"Presta??es com marcador legado: "
            f"{Prestacao.objects.filter(credor__icontains=MARCADOR_LEGADO).count()}"
        )
        self.stdout.write(
            f"Termos vinculados a empresas legadas: "
            f"{Termos.objects.filter(empresa__nome__icontains=MARCADOR_LEGADO).count()}"
        )
