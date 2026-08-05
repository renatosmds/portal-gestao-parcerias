from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.urls import get_resolver


class Command(BaseCommand):
    help = "Verifica banco, migrations, rotas, modelos e limites de campos do PGP."

    def handle(self, *args, **options):
        falhas = []
        self.stdout.write("=== Diagnóstico do Portal de Gestão de Parcerias ===")

        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS("[OK] Banco de dados conectado"))
        except Exception as exc:
            falhas.append(f"Banco: {exc}")
            self.stdout.write(self.style.ERROR(f"[ERRO] Banco de dados: {exc}"))

        try:
            executor = MigrationExecutor(connection)
            pendentes = executor.migration_plan(executor.loader.graph.leaf_nodes())
            if pendentes:
                falhas.append(f"{len(pendentes)} migration(s) pendente(s)")
                self.stdout.write(self.style.WARNING(f"[ATENÇÃO] {len(pendentes)} migration(s) pendente(s)"))
            else:
                self.stdout.write(self.style.SUCCESS("[OK] Migrations aplicadas"))
        except Exception as exc:
            falhas.append(f"Migrations: {exc}")

        rotas = {p.name for p in get_resolver().url_patterns if getattr(p, "name", None)}
        essenciais = {"home", "menu", "diagnostico_portal"}
        ausentes = sorted(essenciais - rotas)
        if ausentes:
            falhas.append("Rotas ausentes: " + ", ".join(ausentes))
            self.stdout.write(self.style.ERROR("[ERRO] Rotas ausentes: " + ", ".join(ausentes)))
        else:
            self.stdout.write(self.style.SUCCESS("[OK] Rotas essenciais carregadas"))

        excessos = []
        for model in apps.get_models():
            for field in model._meta.fields:
                limite = getattr(field, "max_length", None)
                if not limite or not hasattr(model, "objects"):
                    continue
                try:
                    for pk, valor in model.objects.exclude(**{f"{field.name}__isnull": True}).values_list("pk", field.name):
                        if isinstance(valor, str) and len(valor) > limite:
                            excessos.append(f"{model._meta.label}.{field.name} pk={pk}: {len(valor)}/{limite}")
                except Exception:
                    continue
        if excessos:
            falhas.extend(excessos)
            self.stdout.write(self.style.ERROR(f"[ERRO] {len(excessos)} valor(es) acima de max_length"))
            for item in excessos[:20]:
                self.stdout.write("  - " + item)
        else:
            self.stdout.write(self.style.SUCCESS("[OK] Nenhum valor acima de max_length"))

        self.stdout.write(f"[INFO] Modelos carregados: {len(list(apps.get_models()))}")
        if falhas:
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("Diagnóstico concluído sem falhas."))
