from django.core.management.base import BaseCommand
from django.db import transaction

from apps.analise.models import Analise
from apps.conciliacao.models import Conciliacao, VinculoConciliacao
from apps.diligencias.models import Diligencia
from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.metas.models import MetaExecucao
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos
from apps.transparencia.models import PublicacaoDocumento


TERMOS_DEMO = ("001/2026", "002/2026", "003/2026")

METAS_ATUAIS = {
    "001/2026": {"M1.1", "M1.2", "M1.3"},
    "002/2026": {"M2.1", "M2.2", "M2.3"},
    "003/2026": {"M3.1", "M3.2", "M3.3"},
}


class Command(BaseCommand):
    help = "Higieniza os registros legados da base demonstrativa."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            "=== HIGIENIZACAO DEFINITIVA DA BASE DEMO ==="
        )

        empresas_atuais = {}

        # A limpeza roda antes da cria??o dos cen?rios atuais.
        # Portanto, zero candidatos ? uma situa??o v?lida.
        # Mais de um candidato "Demo" para o mesmo termo ? que
        # representa ambiguidade e deve interromper a opera??o.
        for numero in TERMOS_DEMO:
            candidatos = Empresa.objects.filter(
                nome__endswith="Demo",
                termos__numtermo=numero,
            )

            quantidade = candidatos.count()

            if quantidade > 1:
                self.stdout.write(
                    self.style.ERROR(
                        f"Cenario atual {numero}: "
                        f"{quantidade} candidatos Demo encontrados."
                    )
                )
                raise RuntimeError(
                    "Existem multiplos cenarios atuais para o mesmo termo."
                )

            if quantidade == 1:
                empresas_atuais[numero] = candidatos.get()

        ids_empresas_atuais = {
            empresa.pk for empresa in empresas_atuais.values()
        }

        self.stdout.write(
            "Cenarios atuais identificados: "
            + ", ".join(
                f"{numero}=empresa#{empresa.pk}"
                for numero, empresa in empresas_atuais.items()
            )
        )

        prestacoes_legadas = Prestacao.objects.filter(
            numtermo__in=TERMOS_DEMO
        ).exclude(
            empresa_id__in=ids_empresas_atuais
        )

        prestacoes_ids = list(
            prestacoes_legadas.values_list("pk", flat=True)
        )

        termos_legados = Termos.objects.filter(
            numtermo__in=TERMOS_DEMO
        ).exclude(
            empresa_id__in=ids_empresas_atuais
        )

        termos_ids = list(
            termos_legados.values_list("pk", flat=True)
        )

        empresas_legadas = Empresa.objects.exclude(
            pk__in=ids_empresas_atuais
        ).filter(
            termos_id__in=termos_ids
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
            f"Empresas antigas vinculadas: {len(empresas_ids)}"
        )

        if prestacoes_ids:
            # 1. Dilig?ncias devem sair antes de documentos/lancamentos,
            # pois tamb?m podem proteg?-los.
            Diligencia.objects.filter(
                prestacao_id__in=prestacoes_ids
            ).delete()

            # 2. Publica??es de documentos dependentes.
            documentos = Documento.objects.filter(
                prestacao_id__in=prestacoes_ids
            )

            PublicacaoDocumento.objects.filter(
                documento__in=documentos
            ).delete()

            # 3. Documentos antes dos lan?amentos.
            documentos.delete()

            # 4. V?nculos de concilia??o que apontam para lan?amentos.
            lancamentos = Lancamento.objects.filter(
                prestacao_id__in=prestacoes_ids
            )

            VinculoConciliacao.objects.filter(
                lancamento__in=lancamentos
            ).delete()

            # 5. Lan?amentos.
            lancamentos.delete()

            # 6. An?lises e metas.
            Analise.objects.filter(
                prestacao_id__in=prestacoes_ids
            ).delete()

            MetaExecucao.objects.filter(
                prestacao_id__in=prestacoes_ids
            ).delete()

            # 7. Concilia??es e suas movimenta??es por cascata.
            Conciliacao.objects.filter(
                prestacao_id__in=prestacoes_ids
            ).delete()

            # 8. Remove refer?ncias PROTECT mantidas por Empresa.
            Empresa.objects.filter(
                prestacao_id__in=prestacoes_ids
            ).update(prestacao=None)

            # 9. Finalmente, presta??es antigas.
            Prestacao.objects.filter(
                pk__in=prestacoes_ids
            ).delete()

        if termos_ids:
            Empresa.objects.filter(
                termos_id__in=termos_ids
            ).update(termos=None)

            Termos.objects.filter(
                pk__in=termos_ids
            ).delete()

        if empresas_ids:
            Empresa.objects.filter(
                pk__in=empresas_ids
            ).delete()

        # Remove metas excedentes dos tr?s cen?rios atuais.
        metas_removidas = 0

        for numero, empresa in empresas_atuais.items():
            prestacao = Prestacao.objects.filter(
                numtermo=numero,
                empresa=empresa,
            ).first()

            if not prestacao:
                continue

            extras = MetaExecucao.objects.filter(
                prestacao=prestacao
            ).exclude(
                codigo__in=METAS_ATUAIS[numero]
            )

            qtd = extras.count()

            if qtd:
                extras.delete()
                metas_removidas += qtd

        self.stdout.write(
            f"Metas excedentes removidas: {metas_removidas}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Higienizacao definitiva concluida."
            )
        )
