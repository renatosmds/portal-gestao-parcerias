from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.template.loader import get_template
from django.urls import reverse


ROTAS_CRITICAS = (
    "home",
    "list_empresas",
    "list_termos",
    "list_prestacao",
    "list_documentos",
    "list_lancamentos",
    "list_analise",
    "list_diligencias",
    "relatorios_painel",
    "assistente_ia_central",
    "transparencia_publica",
    "conciliacao_painel",
    "metas_painel",
)

TEMPLATES_CRITICOS = (
    "base.html",
    "core/index.html",
    "conciliacao/painel.html",
    "metas/painel.html",
)


class Command(BaseCommand):
    help = "Executa verificações rápidas de consolidação do Portal de Gestão de Parcerias."

    def handle(self, *args, **options):
        falhas = []
        self.stdout.write(self.style.MIGRATE_HEADING("PGP — validação consolidada (Sprint 27)"))

        try:
            call_command("check", verbosity=0)
            self.stdout.write(self.style.SUCCESS("[OK] Configuração Django"))
        except Exception as exc:  # pragma: no cover - proteção operacional
            falhas.append(f"Configuração Django: {exc}")
            self.stdout.write(self.style.ERROR(f"[FALHA] Configuração Django: {exc}"))

        for template_name in TEMPLATES_CRITICOS:
            try:
                get_template(template_name)
                self.stdout.write(self.style.SUCCESS(f"[OK] Template: {template_name}"))
            except Exception as exc:
                falhas.append(f"Template {template_name}: {exc}")
                self.stdout.write(self.style.ERROR(f"[FALHA] Template {template_name}: {exc}"))

        for route_name in ROTAS_CRITICAS:
            try:
                url = reverse(route_name)
                self.stdout.write(self.style.SUCCESS(f"[OK] Rota: {route_name} -> {url}"))
            except Exception as exc:
                falhas.append(f"Rota {route_name}: {exc}")
                self.stdout.write(self.style.ERROR(f"[FALHA] Rota {route_name}: {exc}"))

        if falhas:
            self.stdout.write(self.style.ERROR(f"Validação concluída com {len(falhas)} falha(s)."))
            for falha in falhas:
                self.stdout.write(f" - {falha}")
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS("Validação concluída sem falhas críticas."))
