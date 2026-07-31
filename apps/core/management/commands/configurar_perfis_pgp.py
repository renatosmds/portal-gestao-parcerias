from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


PERFIS = {
    "Administrador do Órgão": {
        "modo": "todos",
    },
    "Gestor do Termo": {
        "permissoes": [
            ("empresas", "view_empresa"),
            ("termos", "view_termos"),
            ("termos", "add_termos"),
            ("termos", "change_termos"),
            ("prestacao", "view_prestacao"),
            ("prestacao", "add_prestacao"),
            ("prestacao", "change_prestacao"),
            ("lancamentos", "view_lancamento"),
            ("documentos", "view_documento"),
            ("analise", "view_analise"),
            ("analise", "add_analise"),
            ("analise", "change_analise"),
            ("parcerias", "view_parcerias"),
            ("parcerias", "change_parcerias"),
        ]
    },
    "Analista Técnico": {
        "permissoes": [
            ("empresas", "view_empresa"),
            ("termos", "view_termos"),
            ("prestacao", "view_prestacao"),
            ("lancamentos", "view_lancamento"),
            ("lancamentos", "change_lancamento"),
            ("documentos", "view_documento"),
            ("documentos", "change_documento"),
            ("analise", "view_analise"),
            ("analise", "add_analise"),
            ("analise", "change_analise"),
        ]
    },
    "Fiscal da Parceria": {
        "permissoes": [
            ("empresas", "view_empresa"),
            ("termos", "view_termos"),
            ("prestacao", "view_prestacao"),
            ("lancamentos", "view_lancamento"),
            ("documentos", "view_documento"),
            ("documentos", "change_documento"),
            ("analise", "view_analise"),
            ("parcerias", "view_parcerias"),
        ]
    },
    "Controle Interno": {
        "modo": "visualizacao",
    },
    "Representante Legal da OSC": {
        "permissoes": [
            ("empresas", "view_empresa"),
            ("empresas", "change_empresa"),
            ("fornecedores", "view_fornecedores"),
            ("fornecedores", "add_fornecedores"),
            ("fornecedores", "change_fornecedores"),
            ("termos", "view_termos"),
            ("prestacao", "view_prestacao"),
            ("prestacao", "add_prestacao"),
            ("prestacao", "change_prestacao"),
            ("lancamentos", "view_lancamento"),
            ("lancamentos", "add_lancamento"),
            ("lancamentos", "change_lancamento"),
            ("documentos", "view_documento"),
            ("documentos", "add_documento"),
            ("documentos", "change_documento"),
            ("analise", "view_analise"),
            ("parcerias", "view_parcerias"),
        ]
    },
    "Gestor Financeiro da OSC": {
        "permissoes": [
            ("empresas", "view_empresa"),
            ("fornecedores", "view_fornecedores"),
            ("fornecedores", "add_fornecedores"),
            ("fornecedores", "change_fornecedores"),
            ("termos", "view_termos"),
            ("prestacao", "view_prestacao"),
            ("prestacao", "add_prestacao"),
            ("prestacao", "change_prestacao"),
            ("lancamentos", "view_lancamento"),
            ("lancamentos", "add_lancamento"),
            ("lancamentos", "change_lancamento"),
            ("documentos", "view_documento"),
            ("documentos", "add_documento"),
            ("documentos", "change_documento"),
        ]
    },
    "Contador da OSC": {
        "permissoes": [
            ("empresas", "view_empresa"),
            ("fornecedores", "view_fornecedores"),
            ("fornecedores", "add_fornecedores"),
            ("fornecedores", "change_fornecedores"),
            ("termos", "view_termos"),
            ("prestacao", "view_prestacao"),
            ("prestacao", "add_prestacao"),
            ("prestacao", "change_prestacao"),
            ("lancamentos", "view_lancamento"),
            ("lancamentos", "add_lancamento"),
            ("lancamentos", "change_lancamento"),
            ("documentos", "view_documento"),
            ("documentos", "add_documento"),
            ("documentos", "change_documento"),
        ]
    },
}

APPS_PGP = {
    "empresas",
    "fornecedores",
    "termos",
    "prestacao",
    "lancamentos",
    "documentos",
    "analise",
    "parcerias",
}


class Command(BaseCommand):
    help = "Cria ou atualiza os perfis padrão do Portal de Gestão de Parcerias."

    def handle(self, *args, **options):
        for nome, configuracao in PERFIS.items():
            grupo, criado = Group.objects.get_or_create(name=nome)

            if configuracao.get("modo") == "todos":
                permissoes = Permission.objects.filter(
                    content_type__app_label__in=APPS_PGP
                )
            elif configuracao.get("modo") == "visualizacao":
                permissoes = Permission.objects.filter(
                    content_type__app_label__in=APPS_PGP,
                    codename__startswith="view_",
                )
            else:
                permissoes = Permission.objects.none()
                faltantes = []
                for app_label, codename in configuracao.get("permissoes", []):
                    permissao = Permission.objects.filter(
                        content_type__app_label=app_label,
                        codename=codename,
                    ).first()
                    if permissao:
                        permissoes = permissoes | Permission.objects.filter(pk=permissao.pk)
                    else:
                        faltantes.append(f"{app_label}.{codename}")
                if faltantes:
                    self.stdout.write(
                        self.style.WARNING(
                            f"{nome}: permissões não localizadas: {', '.join(faltantes)}"
                        )
                    )

            grupo.permissions.set(permissoes.distinct())
            acao = "criado" if criado else "atualizado"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Perfil {acao}: {nome} ({grupo.permissions.count()} permissões)"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Perfis do PGP configurados. Vincule cada usuário ao grupo e à OSC correta."
            )
        )
