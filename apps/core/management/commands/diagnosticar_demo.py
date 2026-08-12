from django.core.management.base import BaseCommand
from django.db.models import Count, Sum

from apps.empresas.models import Empresa
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos
from apps.lancamentos.models import Lancamento
from apps.metas.models import MetaExecucao
from apps.diligencias.models import Diligencia


class Command(BaseCommand):
    help = "Diagnostica registros existentes na base demonstrativa."

    def handle(self, *args, **options):

        self.stdout.write("")
        self.stdout.write("=== EMPRESAS ===")

        for e in Empresa.objects.all().order_by("pk"):
            self.stdout.write(
                f"ID={e.pk} | nome={e.nome!r} | "
                f"prestacao_id={e.prestacao_id} | termos_id={e.termos_id}"
            )

        self.stdout.write("")
        self.stdout.write("=== TERMOS ===")

        for t in Termos.objects.all().order_by("numtermo", "pk"):
            self.stdout.write(
                f"ID={t.pk} | termo={t.numtermo!r} | "
                f"empresa_id={t.empresa_id} | "
                f"empresa={getattr(t.empresa, 'nome', None)!r} | "
                f"global={t.valorglobal} | saldo={t.valorsaldo}"
            )

        self.stdout.write("")
        self.stdout.write("=== PRESTACOES ===")

        for p in Prestacao.objects.all().order_by("numtermo", "pk"):
            self.stdout.write(
                f"ID={p.pk} | termo={p.numtermo!r} | "
                f"empresa_id={p.empresa_id} | "
                f"credor={p.credor!r} | "
                f"valor={p.valorContrato} | "
                f"workflow={p.situacao_workflow} | "
                f"lancamentos={Lancamento.objects.filter(prestacao=p).count()} | "
                f"metas={MetaExecucao.objects.filter(prestacao=p).count()} | "
                f"diligencias={Diligencia.objects.filter(prestacao=p).count()}"
            )

        self.stdout.write("")
        self.stdout.write("=== DUPLICIDADES POR NUMERO DE TERMO ===")

        duplicados = (
            Prestacao.objects
            .values("numtermo")
            .annotate(qtd=Count("id"))
            .filter(qtd__gt=1)
            .order_by("numtermo")
        )

        for item in duplicados:
            self.stdout.write(
                f"{item['numtermo']!r}: {item['qtd']} prestacoes"
            )

        self.stdout.write("")
        self.stdout.write("=== TOTAIS ===")

        total_global = (
            Termos.objects.aggregate(v=Sum("valorglobal"))["v"] or 0
        )

        total_executado = (
            Lancamento.objects.aggregate(v=Sum("valor_documento"))["v"] or 0
        )

        total_glosa = (
            Lancamento.objects.aggregate(v=Sum("valor_glosa"))["v"] or 0
        )

        self.stdout.write(f"Empresas: {Empresa.objects.count()}")
        self.stdout.write(f"Termos: {Termos.objects.count()}")
        self.stdout.write(f"Prestacoes: {Prestacao.objects.count()}")
        self.stdout.write(f"Lancamentos: {Lancamento.objects.count()}")
        self.stdout.write(f"Metas: {MetaExecucao.objects.count()}")
        self.stdout.write(f"Diligencias: {Diligencia.objects.count()}")
        self.stdout.write(f"Valor global: {total_global}")
        self.stdout.write(f"Valor executado: {total_executado}")
        self.stdout.write(f"Valor glosado: {total_glosa}")
