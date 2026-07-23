from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand, CommandError


PERFIS = {
    "Administrador": {
        "funcionarios": {
            "add_funcionario",
            "change_funcionario",
            "delete_funcionario",
            "view_funcionario",
        },
        "empresas": {
            "add_empresa",
            "change_empresa",
            "delete_empresa",
            "view_empresa",
        },
    },
    "Gestor": {
        "funcionarios": {
            "add_funcionario",
            "change_funcionario",
            "view_funcionario",
        },
        "empresas": {
            "change_empresa",
            "view_empresa",
        },
    },
    "Analista": {
        "funcionarios": {"view_funcionario"},
        "empresas": {"view_empresa"},
    },
    "Usuário": {
        "funcionarios": set(),
        "empresas": {"view_empresa"},
    },
}


class Command(BaseCommand):
    help = "Cria ou atualiza os perfis-padrão do SGM."

    def add_arguments(self, parser):
        parser.add_argument(
            "--administrador",
            dest="administrador",
            help="Username que receberá o perfil Administrador.",
        )

    def handle(self, *args, **options):
        for nome, apps in PERFIS.items():
            grupo, _ = Group.objects.get_or_create(name=nome)
            permissoes = Permission.objects.none()

            for app_label, codenames in apps.items():
                permissoes = permissoes | Permission.objects.filter(
                    content_type__app_label=app_label,
                    codename__in=codenames,
                )

            grupo.permissions.set(permissoes.distinct())
            self.stdout.write(
                self.style.SUCCESS(
                    f"Perfil '{nome}' atualizado com "
                    f"{grupo.permissions.count()} permissão(ões)."
                )
            )

        username = options.get("administrador")
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist as exc:
                raise CommandError(
                    f"Usuário '{username}' não encontrado."
                ) from exc

            user.groups.add(Group.objects.get(name="Administrador"))
            self.stdout.write(
                self.style.SUCCESS(
                    f"Perfil Administrador atribuído a '{username}'."
                )
            )
