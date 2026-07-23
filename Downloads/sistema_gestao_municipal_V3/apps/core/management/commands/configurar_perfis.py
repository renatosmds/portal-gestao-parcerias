from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand, CommandError


PERFIS = {
    "Administrador": {
        "add_funcionario",
        "change_funcionario",
        "delete_funcionario",
        "view_funcionario",
    },
    "Gestor": {
        "add_funcionario",
        "change_funcionario",
        "view_funcionario",
    },
    "Analista": {
        "view_funcionario",
    },
    "Usuário": set(),
}


class Command(BaseCommand):
    help = "Cria os perfis-padrão e pode atribuir Administrador a um usuário."

    def add_arguments(self, parser):
        parser.add_argument(
            "--administrador",
            dest="administrador",
            help="Username que receberá o perfil Administrador.",
        )

    def handle(self, *args, **options):
        for nome, codenames in PERFIS.items():
            grupo, _ = Group.objects.get_or_create(name=nome)
            permissoes = Permission.objects.filter(
                content_type__app_label="funcionarios",
                codename__in=codenames,
            )
            grupo.permissions.set(permissoes)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Perfil '{nome}' configurado com {permissoes.count()} permissão(ões)."
                )
            )

        username = options.get("administrador")
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist as exc:
                raise CommandError(f"Usuário '{username}' não encontrado.") from exc

            user.groups.add(Group.objects.get(name="Administrador"))
            self.stdout.write(
                self.style.SUCCESS(
                    f"Perfil Administrador atribuído ao usuário '{username}'."
                )
            )

        self.stdout.write(
            self.style.WARNING(
                "Revise os usuários no Django Admin e atribua um dos quatro perfis."
            )
        )
