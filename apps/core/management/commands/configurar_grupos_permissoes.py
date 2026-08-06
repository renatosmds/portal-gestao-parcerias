from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


GRUPOS = {
    "Administrador do Sistema": {
        "todas": True,
    },

    "Gestor Municipal": {
        "apps_completos": [
            "parcerias",
            "termos",
            "prestacao",
            "metas",
            "diligencias",
            "analise",
            "documentos",
            "conciliacao",
            "transparencia",
        ],
        "apps_visualizacao": [
            "empresas",
            "fornecedores",
            "funcionarios",
            "departamentos",
            "assistente_ia",
            "ajuda_contextual",
        ],
    },

    "Analista de Prestação de Contas": {
        "apps_completos": [
            "prestacao",
            "analise",
            "documentos",
            "diligencias",
            "conciliacao",
            "fornecedores",
        ],
        "apps_visualizacao": [
            "parcerias",
            "termos",
            "empresas",
            "metas",
            "transparencia",
        ],
    },

    "Técnico de Execução": {
        "apps_completos": [
            "metas",
            "documentos",
            "diligencias",
        ],
        "apps_visualizacao": [
            "parcerias",
            "termos",
            "prestacao",
            "empresas",
            "analise",
        ],
    },

    "Financeiro": {
        "apps_completos": [
            "prestacao",
            "conciliacao",
            "documentos",
            "fornecedores",
        ],
        "apps_visualizacao": [
            "parcerias",
            "termos",
            "empresas",
            "metas",
            "analise",
        ],
    },

    "Usuário da OSC": {
        "apps_inclusao_alteracao_visualizacao": [
            "prestacao",
            "documentos",
            "metas",
            "diligencias",
        ],
        "apps_visualizacao": [
            "parcerias",
            "termos",
            "empresas",
        ],
    },

    "Consulta e Auditoria": {
        "somente_visualizacao_global": True,
    },
}


class Command(BaseCommand):
    help = "Cria os grupos funcionais e atribui permissões ao Portal."

    def permissoes_app(self, app_label, prefixos):
        consulta = Permission.objects.filter(
            content_type__app_label=app_label
        )

        if prefixos:
            consulta = consulta.filter(
                codename__regex=rf"^({'|'.join(prefixos)})_"
            )

        return consulta

    def handle(self, *args, **options):
        for nome_grupo, configuracao in GRUPOS.items():
            grupo, criado = Group.objects.get_or_create(name=nome_grupo)

            # Torna o comando idempotente:
            # cada execução recalcula as permissões do grupo.
            grupo.permissions.clear()

            if configuracao.get("todas"):
                grupo.permissions.set(Permission.objects.all())

            elif configuracao.get("somente_visualizacao_global"):
                grupo.permissions.set(
                    Permission.objects.filter(codename__startswith="view_")
                )

            else:
                for app_label in configuracao.get("apps_completos", []):
                    grupo.permissions.add(
                        *self.permissoes_app(
                            app_label,
                            ["add", "change", "delete", "view"],
                        )
                    )

                for app_label in configuracao.get(
                    "apps_inclusao_alteracao_visualizacao", []
                ):
                    grupo.permissions.add(
                        *self.permissoes_app(
                            app_label,
                            ["add", "change", "view"],
                        )
                    )

                for app_label in configuracao.get("apps_visualizacao", []):
                    grupo.permissions.add(
                        *self.permissoes_app(
                            app_label,
                            ["view"],
                        )
                    )

            situacao = "criado" if criado else "atualizado"

            self.stdout.write(
                self.style.SUCCESS(
                    f"{nome_grupo}: {situacao} "
                    f"com {grupo.permissions.count()} permissões."
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Grupos e permissões configurados com sucesso."
            )
        )
