import calendar
from collections import defaultdict
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from apps.lancamentos.models import Lancamento
from apps.prestacao.models import CompetenciaPrestacao


class Command(BaseCommand):
    help = (
        "Cria competencias mensais e vincula apenas os lancamentos "
        "da base demonstrativa do PGP."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--aplicar",
            action="store_true",
            help="Efetiva as alteracoes. Sem esta opcao roda em simulacao.",
        )

    def handle(self, *args, **options):
        aplicar = options["aplicar"]

        filtro_demo = (
            Q(empresa__nome__icontains="demo")
            | Q(empresa__nome__icontains="demonstrativo")
            | Q(empresa__nome__icontains="demonstracao")
        )

        lancamentos = (
            Lancamento.objects
            .filter(filtro_demo)
            .select_related("empresa", "prestacao")
            .order_by(
                "empresa__nome",
                "prestacao_id",
                "data_documento",
                "id",
            )
        )

        total = lancamentos.count()

        self.stdout.write(
            f"Modo: {'APLICACAO' if aplicar else 'SIMULACAO'}"
        )
        self.stdout.write(
            f"Lancamentos demonstrativos encontrados: {total}"
        )

        if not total:
            self.stdout.write(
                self.style.WARNING(
                    "Nenhum lancamento demonstrativo encontrado."
                )
            )
            return

        empresas = (
            lancamentos
            .order_by()
            .values_list("empresa__nome", flat=True)
            .distinct()
            .order_by("empresa__nome")
        )

        self.stdout.write("Empresas demonstrativas:")
        for nome in empresas:
            self.stdout.write(f"  - {nome}")

        sem_prestacao = lancamentos.filter(prestacao__isnull=True).count()

        if sem_prestacao:
            self.stdout.write(
                self.style.WARNING(
                    f"Lancamentos sem prestacao: {sem_prestacao}"
                )
            )

        grupos = defaultdict(list)

        for lancamento in lancamentos:
            if not lancamento.prestacao_id:
                continue

            data_doc = lancamento.data_documento
            chave = (
                lancamento.prestacao_id,
                data_doc.year,
                data_doc.month,
            )
            grupos[chave].append(lancamento)

        self.stdout.write(
            f"Competencias mensais identificadas: {len(grupos)}"
        )

        for (prestacao_id, ano, mes), itens in grupos.items():
            self.stdout.write(
                f"  Prestacao {prestacao_id} - "
                f"{mes:02d}/{ano}: {len(itens)} lancamento(s)"
            )

        if not aplicar:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "SIMULACAO concluida. "
                    "Nenhuma alteracao foi gravada."
                )
            )
            self.stdout.write(
                "Para efetivar, execute novamente com --aplicar."
            )
            return

        competencias_criadas = 0
        competencias_existentes = 0
        vinculados = 0

        with transaction.atomic():
            for (prestacao_id, ano, mes), itens in grupos.items():
                ultimo_dia = calendar.monthrange(ano, mes)[1]

                competencia, criada = (
                    CompetenciaPrestacao.objects.get_or_create(
                        prestacao_id=prestacao_id,
                        ano=ano,
                        mes=mes,
                        defaults={
                            "data_inicial": date(ano, mes, 1),
                            "data_final": date(
                                ano,
                                mes,
                                ultimo_dia,
                            ),
                            "saldo_inicial": 0,
                            "saldo_final": 0,
                            "status": (
                                CompetenciaPrestacao.Status.ABERTA
                            ),
                        },
                    )
                )

                if criada:
                    competencias_criadas += 1
                else:
                    competencias_existentes += 1

                ids = [item.id for item in itens]

                atualizados = (
                    Lancamento.objects
                    .filter(
                        id__in=ids,
                        prestacao_id=prestacao_id,
                    )
                    .exclude(
                        competencia_id=competencia.id
                    )
                    .update(
                        competencia=competencia
                    )
                )

                vinculados += atualizados

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Base demonstrativa atualizada com sucesso."
            )
        )
        self.stdout.write(
            f"Competencias criadas: {competencias_criadas}"
        )
        self.stdout.write(
            f"Competencias ja existentes: {competencias_existentes}"
        )
        self.stdout.write(
            f"Lancamentos vinculados/atualizados: {vinculados}"
        )
