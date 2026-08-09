import re
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import connection
from django.urls import get_resolver


class Command(BaseCommand):
    help = "Executa validacoes basicas antes do deploy em producao."

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("VALIDACAO DE PRODUCAO")
        self.stdout.write("=" * 70)

        falhas = []

        # 1. Verificacao geral do Django
        try:
            call_command("check")
            self.stdout.write(self.style.SUCCESS("[OK] Django check"))
        except Exception as exc:
            falhas.append(f"Django check: {exc}")
            self.stdout.write(self.style.ERROR(f"[ERRO] Django check: {exc}"))

        # 2. Banco de dados
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            self.stdout.write(self.style.SUCCESS("[OK] Banco de dados"))
        except Exception as exc:
            falhas.append(f"Banco de dados: {exc}")
            self.stdout.write(self.style.ERROR(f"[ERRO] Banco de dados: {exc}"))

        # 3. URLConf
        try:
            resolver = get_resolver()
            quantidade_urls = len(resolver.url_patterns)

            self.stdout.write(
                self.style.SUCCESS(
                    f"[OK] URLs carregadas ({quantidade_urls} rotas principais)"
                )
            )
        except Exception as exc:
            falhas.append(f"URLs: {exc}")
            self.stdout.write(self.style.ERROR(f"[ERRO] URLs: {exc}"))

        # 4. Diretorio STATIC_ROOT
        try:
            static_root = Path(settings.STATIC_ROOT)

            if static_root.exists():
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[OK] STATIC_ROOT encontrado: {static_root}"
                    )
                )
            else:
                falhas.append(
                    f"STATIC_ROOT nao encontrado: {static_root}"
                )
                self.stdout.write(
                    self.style.ERROR(
                        f"[ERRO] STATIC_ROOT nao encontrado: {static_root}"
                    )
                )
        except Exception as exc:
            falhas.append(f"STATIC_ROOT: {exc}")
            self.stdout.write(self.style.ERROR(f"[ERRO] STATIC_ROOT: {exc}"))

        # 5. Referencias {% static %} nos templates
        self.validar_static_templates(falhas)

        # Resultado final
        self.stdout.write("")
        self.stdout.write("-" * 70)

        if falhas:
            self.stdout.write(
                self.style.ERROR(
                    f"VALIDACAO CONCLUIDA COM {len(falhas)} PROBLEMA(S)"
                )
            )

            for falha in falhas:
                self.stdout.write(self.style.ERROR(f"- {falha}"))

            raise SystemExit(1)

        self.stdout.write(
            self.style.SUCCESS(
                "VALIDACAO DE PRODUCAO CONCLUIDA COM SUCESSO"
            )
        )

    def validar_static_templates(self, falhas):
        raiz = Path(settings.BASE_DIR)

        pastas_templates = []

        pasta_global = raiz / "templates"
        if pasta_global.exists():
            pastas_templates.append(pasta_global)

        for pasta in raiz.glob("apps/*/templates"):
            if pasta.exists():
                pastas_templates.append(pasta)

        for pasta in raiz.glob("*/templates"):
            if pasta.exists() and pasta not in pastas_templates:
                pastas_templates.append(pasta)

        padrao = re.compile(
            r"""{%\s*static\s+['"]([^'"]+)['"]\s*%}"""
        )

        problemas = []

        for pasta_templates in pastas_templates:
            for template in pasta_templates.rglob("*.html"):
                try:
                    conteudo = template.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    )
                except Exception:
                    continue

                for caminho_static in padrao.findall(conteudo):
                    encontrado = False

                    for static_dir in settings.STATICFILES_DIRS:
                        candidato = Path(static_dir) / caminho_static
                        if candidato.exists():
                            encontrado = True
                            break

                    if not encontrado:
                        candidato_root = Path(settings.STATIC_ROOT) / caminho_static

                        if candidato_root.exists():
                            encontrado = True

                    if not encontrado:
                        problemas.append(
                            (
                                template.relative_to(raiz),
                                caminho_static,
                            )
                        )

        if problemas:
            self.stdout.write(
                self.style.ERROR(
                    f"[ERRO] {len(problemas)} referencia(s) static inexistente(s)"
                )
            )

            for template, caminho in problemas:
                self.stdout.write(
                    self.style.ERROR(
                        f"       {template} -> {caminho}"
                    )
                )

            falhas.append(
                f"{len(problemas)} referencia(s) static inexistente(s)"
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "[OK] Referencias static dos templates"
                )
            )