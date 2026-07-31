from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Mostra usuários, perfis e vínculos Funcionario/Empresa."

    def handle(self, *args, **options):
        self.stdout.write("DIAGNÓSTICO DE ACESSOS")
        self.stdout.write("-" * 72)

        for user in User.objects.order_by("username"):
            groups = ", ".join(user.groups.values_list("name", flat=True))
            groups = groups or ("Administrador (superuser)" if user.is_superuser else "Sem perfil")

            funcionario_nome = "Não vinculado"
            empresa_nome = "Não vinculada"

            try:
                funcionario = user.funcionario
                if funcionario:
                    funcionario_nome = str(funcionario)
                    if funcionario.empresa_id:
                        empresa_nome = str(funcionario.empresa)
            except Exception:
                pass

            self.stdout.write(
                f"{user.username} | perfil: {groups} | "
                f"funcionário: {funcionario_nome} | empresa: {empresa_nome}"
            )
