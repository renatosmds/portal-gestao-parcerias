import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Cria ou atualiza os dados fictícios do ambiente demonstrativo."

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("DEMO_ADMIN_USERNAME", "demo_admin")
        password = os.getenv("DEMO_ADMIN_PASSWORD", "")
        email = os.getenv("DEMO_ADMIN_EMAIL", "demo@exemplo.invalid")

        user, _ = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed = False

        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            changed = True

        if password:
            user.set_password(password)
            changed = True

        if changed:
            user.save()

        call_command("limpar_demo_legado")
        call_command("preparar_demo_ciclo_completo")

        self.stdout.write(
            self.style.SUCCESS(
                "Ambiente demonstrativo preparado com sucesso."
            )
        )

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    "DEMO_ADMIN_PASSWORD nao foi definida; "
                    "a conta demo nao recebeu senha nova."
                )
            )
