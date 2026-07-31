from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand, CommandError


PERFIS = {
    "Administrador": {
        "funcionarios": {"add_funcionario", "change_funcionario", "delete_funcionario", "view_funcionario"},
        "empresas": {"add_empresa", "change_empresa", "delete_empresa", "view_empresa"},
        "departamentos": {"add_departamento", "change_departamento", "delete_departamento", "view_departamento"},
        "fornecedores": {"add_fornecedores", "change_fornecedores", "delete_fornecedores", "view_fornecedores"},
        "parcerias": {"add_parcerias", "change_parcerias", "delete_parcerias", "view_parcerias"},
        "termos": {"add_termos", "change_termos", "delete_termos", "view_termos"},
        "prestacao": {"add_prestacao", "change_prestacao", "delete_prestacao", "view_prestacao"},
        "analise": {"add_analise", "change_analise", "delete_analise", "view_analise"},
        "lancamentos": {"add_lancamento", "change_lancamento", "delete_lancamento", "view_lancamento"},
        "documentos": {"add_documento", "change_documento", "delete_documento", "view_documento"},
    },
    "Gestor": {
        "funcionarios": {"add_funcionario", "change_funcionario", "view_funcionario"},
        "empresas": {"change_empresa", "view_empresa"},
        "departamentos": {"add_departamento", "change_departamento", "view_departamento"},
        "fornecedores": {"add_fornecedores", "change_fornecedores", "view_fornecedores"},
        "parcerias": {"add_parcerias", "change_parcerias", "view_parcerias"},
        "termos": {"add_termos", "change_termos", "view_termos"},
        "prestacao": {"add_prestacao", "change_prestacao", "view_prestacao"},
        "analise": {"add_analise", "change_analise", "view_analise"},
        "lancamentos": {"add_lancamento", "change_lancamento", "view_lancamento"},
        "documentos": {"add_documento", "change_documento", "view_documento"},
    },
    "Analista": {
        "funcionarios": {"view_funcionario"},
        "empresas": {"view_empresa"},
        "departamentos": {"view_departamento"},
        "fornecedores": {"view_fornecedores"},
        "parcerias": {"view_parcerias"},
        "termos": {"view_termos"},
        "prestacao": {"view_prestacao"},
        "analise": {"view_analise"},
        "lancamentos": {"view_lancamento"},
        "documentos": {"view_documento"},
        "termos": {"view_termos"},
        "prestacao": {"view_prestacao"},
        "analise": {"view_analise"},
        "lancamentos": {"view_lancamento"},
    },
    "Usuário": {
        "funcionarios": set(),
        "empresas": {"view_empresa"},
        "departamentos": {"view_departamento"},
        "fornecedores": {"view_fornecedores"},
        "parcerias": {"view_parcerias"},
        "documentos": {"view_documento"},
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
