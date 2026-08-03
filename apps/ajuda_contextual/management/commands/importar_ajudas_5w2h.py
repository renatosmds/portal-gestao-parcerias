import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from apps.ajuda_contextual.models import AjudaContextual

class Command(BaseCommand):
    help = "Importa ou atualiza orientações 5W2H a partir de JSON."
    def add_arguments(self, parser):
        parser.add_argument("arquivo", nargs="?", default=str(Path(__file__).resolve().parents[2] / "dados_iniciais" / "ajudas_5w2h.json"))
    def handle(self, *args, **options):
        path=Path(options["arquivo"])
        if not path.exists(): raise CommandError(f"Arquivo não encontrado: {path}")
        dados=json.loads(path.read_text(encoding="utf-8")); criados=atualizados=0
        for item in dados:
            chave=item.pop("chave")
            _, criado=AjudaContextual.objects.update_or_create(chave=chave, defaults=item)
            criados += int(criado); atualizados += int(not criado)
        self.stdout.write(self.style.SUCCESS(f"Ajudas importadas: {criados} novas, {atualizados} atualizadas."))
