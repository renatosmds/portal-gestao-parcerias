import os
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.management.commands.configurar_grupos_permissoes import (
    GRUPOS as GRUPOS_CONFIGURADOS,
)
from apps.departamentos.models import Departamento
from apps.empresas.models import Empresa
from apps.funcionarios.models import Cargo, Equipamento, Funcionario, Nivel


EMPRESA_NOME = "Prefeitura de Contagem"

QUANTIDADES_INICIAIS = {
    "departamentos": 32,
    "cargos": 39,
    "niveis": 32,
    "equipamentos": 5,
    "funcionarios": 0,
}

GRUPOS_OBRIGATORIOS = set(GRUPOS_CONFIGURADOS)


class Command(BaseCommand):
    help = (
        "Inicializa com seguranca o ambiente real de producao "
        "do Portal de Gestao de Parcerias."
    )

    def _validar_ambiente(self):
        if settings.DEBUG:
            raise CommandError(
                "preparar_producao recusado: DEBUG=True."
            )

        if getattr(
            settings,
            "PGP_AMBIENTE_DEMO",
            False,
        ):
            raise CommandError(
                "preparar_producao recusado: "
                "PGP_AMBIENTE_DEMO=True."
            )

    def _fixture_path(self):
        return (
            Path(settings.BASE_DIR)
            / "dados_iniciais"
            / "estrutura_contagem.json"
        )

    def _quantidades(self, empresa):
        return {
            "departamentos": Departamento.objects.filter(
                empresa=empresa
            ).count(),
            "cargos": Cargo.objects.filter(
                empresa=empresa
            ).count(),
            "niveis": Nivel.objects.filter(
                empresa=empresa
            ).count(),
            "equipamentos": Equipamento.objects.filter(
                empresa=empresa
            ).count(),
            "funcionarios": Funcionario.objects.filter(
                empresa=empresa
            ).count(),
        }

    def _validar_carga_inicial(self, empresa):
        atual = self._quantidades(
            empresa
        )

        if atual != QUANTIDADES_INICIAIS:
            raise CommandError(
                "A estrutura inicial carregada nao corresponde "
                "a carga homologada. "
                f"Encontrado: {atual}."
            )

    def _preparar_estrutura(self):
        empresa = Empresa.objects.filter(
            nome__iexact=EMPRESA_NOME
        ).first()

        if Empresa.objects.exists():
            if not empresa:
                raise CommandError(
                    "O banco ja possui dados, mas a "
                    "Prefeitura de Contagem nao foi encontrada. "
                    "Inicializacao automatica interrompida."
                )

            self.stdout.write(
                "Banco de producao ja inicializado. "
                "Fixture estrutural nao reaplicada."
            )

            return empresa

        fixture = self._fixture_path()

        if not fixture.exists():
            raise CommandError(
                "Fixture estrutural nao encontrada: "
                f"{fixture}"
            )

        self.stdout.write(
            "Banco sem empresas. "
            "Carregando estrutura inicial de Contagem..."
        )

        call_command(
            "loaddata",
            str(fixture),
        )

        empresa = Empresa.objects.filter(
            nome__iexact=EMPRESA_NOME
        ).first()

        if not empresa:
            raise CommandError(
                "Fixture carregada, mas a Prefeitura "
                "de Contagem nao foi encontrada."
            )

        self._validar_carga_inicial(
            empresa
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Estrutura inicial de Contagem "
                "carregada e validada."
            )
        )

        return empresa

    def _configurar_grupos(self):
        self.stdout.write(
            "Configurando grupos e permissoes funcionais..."
        )

        call_command(
            "configurar_grupos_permissoes"
        )

        existentes = set(
            Group.objects.filter(
                name__in=GRUPOS_OBRIGATORIOS
            ).values_list(
                "name",
                flat=True,
            )
        )

        faltantes = (
            GRUPOS_OBRIGATORIOS
            - existentes
        )

        if faltantes:
            raise CommandError(
                "Grupos obrigatorios nao foram criados: "
                + ", ".join(
                    sorted(faltantes)
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Grupos funcionais configurados."
            )
        )

    def _preparar_admin(self):
        username = os.getenv(
            "PGP_ADMIN_USERNAME",
            "",
        ).strip()

        email = os.getenv(
            "PGP_ADMIN_EMAIL",
            "",
        ).strip()

        password = os.getenv(
            "PGP_ADMIN_PASSWORD",
            "",
        )

        if not username:
            raise CommandError(
                "PGP_ADMIN_USERNAME nao definido."
            )

        User = get_user_model()

        user = User.objects.filter(
            username=username
        ).first()

        if user:
            if not (
                user.is_active
                and user.is_staff
                and user.is_superuser
            ):
                raise CommandError(
                    "O usuario administrativo ja existe, "
                    "mas nao possui o perfil esperado. "
                    "Nenhuma alteracao automatica foi feita."
                )

            self.stdout.write(
                "Administrador de producao ja existe. "
                "Senha nao foi alterada."
            )

        else:
            if not password:
                raise CommandError(
                    "PGP_ADMIN_PASSWORD e obrigatoria "
                    "na primeira inicializacao."
                )

            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "Administrador inicial de producao criado."
                )
            )

        grupo_admin = Group.objects.get(
            name="Administrador do Sistema"
        )

        if not user.groups.filter(
            pk=grupo_admin.pk
        ).exists():
            user.groups.add(
                grupo_admin
            )

            self.stdout.write(
                "Administrador vinculado ao grupo "
                "'Administrador do Sistema'."
            )

        return user

    @transaction.atomic
    def handle(self, *args, **options):
        self._validar_ambiente()

        empresa = self._preparar_estrutura()

        self._configurar_grupos()

        admin = self._preparar_admin()

        quantidades = self._quantidades(
            empresa
        )

        self.stdout.write("")
        self.stdout.write(
            "Resumo da inicializacao:"
        )
        self.stdout.write(
            f"Empresa principal: {empresa.nome}"
        )
        self.stdout.write(
            f"Empresas no banco: "
            f"{Empresa.objects.count()}"
        )
        self.stdout.write(
            f"Departamentos Contagem: "
            f"{quantidades['departamentos']}"
        )
        self.stdout.write(
            f"Cargos Contagem: "
            f"{quantidades['cargos']}"
        )
        self.stdout.write(
            f"Niveis Contagem: "
            f"{quantidades['niveis']}"
        )
        self.stdout.write(
            f"Equipamentos Contagem: "
            f"{quantidades['equipamentos']}"
        )
        self.stdout.write(
            f"Funcionarios Contagem: "
            f"{quantidades['funcionarios']}"
        )
        self.stdout.write(
            f"Grupos funcionais: "
            f"{len(GRUPOS_OBRIGATORIOS)}"
        )
        self.stdout.write(
            f"Administrador: {admin.username}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Ambiente de producao preparado "
                "com sucesso."
            )
        )
