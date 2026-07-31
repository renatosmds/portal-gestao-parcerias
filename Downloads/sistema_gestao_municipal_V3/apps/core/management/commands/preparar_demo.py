from decimal import Decimal
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.empresas.models import Empresa
from apps.termos.models import Termos
from apps.prestacao.models import Prestacao


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
            defaults={"email": email, "is_staff": True, "is_superuser": True},
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

        empresa, _ = Empresa.objects.get_or_create(nome="Instituto Caminhos — Demonstração")
        termo, _ = Termos.objects.get_or_create(
            numtermo="001/2026",
            defaults={
                "nomeosc": empresa.nome,
                "termo": "Termo de Colaboração nº 001/2026",
                "tipo": "Termo de Colaboração",
                "objeto": "Atendimento socioassistencial demonstrativo",
                "vigencia": "01/01/2026 a 31/12/2026",
                "valorglobal": Decimal("240000.00"),
                "valorrepasse": Decimal("120000.00"),
                "valorsaldo": Decimal("120000.00"),
                "status": "Vigente",
                "empresa": empresa,
            },
        )
        if termo.empresa_id is None:
            termo.empresa = empresa
            termo.save(update_fields=["empresa"])

        prestacao, _ = Prestacao.objects.get_or_create(
            numtermo="001/2026",
            defaults={
                "tipo": "cnpj",
                "tipoTermo": "TC",
                "credor": empresa.nome,
                "CpfCnpj": "00.000.000/0001-00",
                "valorContrato": 240000.00,
                "situacao_workflow": "em_analise",
            },
        )
        if empresa.prestacao_id is None:
            empresa.prestacao = prestacao
            empresa.termos = termo
            empresa.save(update_fields=["prestacao", "termos"])

        self.stdout.write(self.style.SUCCESS("Ambiente demonstrativo preparado com sucesso."))
        if not password:
            self.stdout.write(self.style.WARNING(
                "DEMO_ADMIN_PASSWORD não foi definida; a conta demo não recebeu senha nova."
            ))
