from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.departamentos.models import Departamento
from apps.empresas.models import Empresa


class Command(BaseCommand):
    help = (
        "Carrega a estrutura organizacional da SMDSSA "
        "sem duplicar unidades."
    )

    EMPRESA = "Prefeitura de Contagem"

    SECRETARIA = (
        "Secretaria Municipal de Desenvolvimento Social "
        "e Seguran\u00e7a Alimentar"
    )

    def obter_unidade(
        self,
        *,
        empresa,
        nome,
        tipo,
        superior,
    ):
        unidade = (
            Departamento.objects
            .filter(
                empresa=empresa,
                nome__iexact=nome,
            )
            .first()
        )

        if unidade:
            alterado = False

            if unidade.tipo != tipo:
                unidade.tipo = tipo
                alterado = True

            if unidade.superior_id != superior.pk:
                unidade.superior = superior
                alterado = True

            if alterado:
                unidade.full_clean()
                unidade.save(
                    update_fields=[
                        "tipo",
                        "superior",
                    ]
                )

            return unidade, False

        unidade = Departamento(
            empresa=empresa,
            nome=nome,
            tipo=tipo,
            superior=superior,
        )

        unidade.full_clean()
        unidade.save()

        return unidade, True

    @transaction.atomic
    def add_arguments(self, parser):
        parser.add_argument(
            "--empresa",
            default=self.EMPRESA,
            help="Nome da empresa onde a estrutura sera criada.",
        )

        parser.add_argument(
            "--secretaria",
            default=self.SECRETARIA,
            help="Nome da unidade raiz da estrutura.",
        )

    def handle(self, *args, **options):
        nome_empresa = options["empresa"]
        nome_secretaria = options["secretaria"]

        empresa = (
            Empresa.objects
            .filter(nome__iexact=nome_empresa)
            .first()
        )

        if not empresa:
            raise CommandError(
                f"Empresa '{nome_empresa}' nao encontrada."
            )

        secretaria = (
            Departamento.objects
            .filter(
                empresa=empresa,
                nome__iexact=nome_secretaria,
            )
            .first()
        )

        if not secretaria:
            raise CommandError(
                f"Unidade raiz '{nome_secretaria}' nao encontrada."
            )

        if secretaria.tipo != Departamento.Tipo.DEPARTAMENTO:
            secretaria.tipo = Departamento.Tipo.DEPARTAMENTO
            secretaria.superior = None
            secretaria.full_clean()
            secretaria.save(
                update_fields=[
                    "tipo",
                    "superior",
                ]
            )

        criados = 0
        atualizados_ou_existentes = 0

        def unidade(nome, tipo, superior):
            nonlocal criados
            nonlocal atualizados_ou_existentes

            obj, criado = self.obter_unidade(
                empresa=empresa,
                nome=nome,
                tipo=tipo,
                superior=superior,
            )

            if criado:
                criados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"CRIADO: {nome}"
                    )
                )
            else:
                atualizados_ou_existentes += 1
                self.stdout.write(
                    f"OK: {nome}"
                )

            return obj

        # Nivel diretamente subordinado a Secretaria.

        unidade(
            "Gabinete do Secret\u00e1rio",
            Departamento.Tipo.GABINETE,
            secretaria,
        )

        unidade(
            "Assessoria de Gest\u00e3o e Inova\u00e7\u00e3o",
            Departamento.Tipo.ASSESSORIA,
            secretaria,
        )

        sup_operacao = unidade(
            "Superintend\u00eancia de Opera\u00e7\u00e3o Institucional",
            Departamento.Tipo.SUPERINTENDENCIA,
            secretaria,
        )

        dir_processos = unidade(
            "Diretoria de Processos Operacionais",
            Departamento.Tipo.DIRETORIA,
            sup_operacao,
        )

        unidade(
            "Ger\u00eancia de Apoio a Compras e Licita\u00e7\u00e3o",
            Departamento.Tipo.GERENCIA,
            dir_processos,
        )

        unidade(
            "Ger\u00eancia de Patrim\u00f4nio e Manuten\u00e7\u00e3o",
            Departamento.Tipo.GERENCIA,
            dir_processos,
        )

        unidade(
            (
                "Ger\u00eancia de Gest\u00e3o de Pessoas "
                "e Apoio Log\u00edstico"
            ),
            Departamento.Tipo.GERENCIA,
            dir_processos,
        )

        unidade(
            "Diretoria de Or\u00e7amento e Finan\u00e7as",
            Departamento.Tipo.DIRETORIA,
            sup_operacao,
        )

        sup_parcerias = unidade(
            "Superintend\u00eancia de Parcerias",
            Departamento.Tipo.SUPERINTENDENCIA,
            secretaria,
        )

        dir_parcerias = unidade(
            (
                "Diretoria de Parceira e "
                "Presta\u00e7\u00e3o de Contas"
            ),
            Departamento.Tipo.DIRETORIA,
            sup_parcerias,
        )

        unidade(
            "Ger\u00eancia de Conv\u00eanios",
            Departamento.Tipo.GERENCIA,
            dir_parcerias,
        )

        unidade(
            "Ger\u00eancia de Presta\u00e7\u00e3o de Contas",
            Departamento.Tipo.GERENCIA,
            dir_parcerias,
        )

        subsecretaria_as = unidade(
            "Subsecretaria de Assist\u00eancia Social",
            Departamento.Tipo.SUBSECRETARIA,
            secretaria,
        )

        sup_as = unidade(
            "Superintend\u00eancia de Assist\u00eancia Social",
            Departamento.Tipo.SUPERINTENDENCIA,
            subsecretaria_as,
        )

        dir_programas = unidade(
            "Diretoria de Programas e Benef\u00edcio",
            Departamento.Tipo.DIRETORIA,
            sup_as,
        )

        unidade(
            "Ger\u00eancia de Cadastro e Atendimento",
            Departamento.Tipo.GERENCIA,
            dir_programas,
        )

        unidade(
            "Diretoria de Prote\u00e7\u00e3o Social B\u00e1sica",
            Departamento.Tipo.DIRETORIA,
            sup_as,
        )

        unidade(
            (
                "Diretoria de Prote\u00e7\u00e3o Social Especial "
                "de M\u00e9dia Complexidade"
            ),
            Departamento.Tipo.DIRETORIA,
            sup_as,
        )

        unidade(
            (
                "Diretoria de Prote\u00e7\u00e3o Social Especial "
                "de Alta Complexidade"
            ),
            Departamento.Tipo.DIRETORIA,
            sup_as,
        )

        dir_suas = unidade(
            (
                "Diretoria de Gest\u00e3o do Sistema \u00danico "
                "da Assist\u00eancia Social \u2013 SUAS"
            ),
            Departamento.Tipo.DIRETORIA,
            sup_as,
        )

        unidade(
            (
                "Ger\u00eancia de Gest\u00e3o de Trabalho "
                "e Educa\u00e7\u00e3o Permanente"
            ),
            Departamento.Tipo.GERENCIA,
            dir_suas,
        )

        unidade(
            "Ger\u00eancia da Vigil\u00e2ncia Socioassistencial",
            Departamento.Tipo.GERENCIA,
            dir_suas,
        )

        unidade(
            "Ger\u00eancia de Regulamenta\u00e7\u00e3o do SUAS",
            Departamento.Tipo.GERENCIA,
            dir_suas,
        )

        subsecretaria_san = unidade(
            (
                "Subsecretaria de Seguran\u00e7a Alimentar, "
                "Nutricional e Agroecologia"
            ),
            Departamento.Tipo.SUBSECRETARIA,
            secretaria,
        )

        sup_san = unidade(
            (
                "Superintend\u00eancia de Seguran\u00e7a Alimentar, "
                "Nutricional e Agroecologia"
            ),
            Departamento.Tipo.SUPERINTENDENCIA,
            subsecretaria_san,
        )

        dir_producao = unidade(
            (
                "Diretoria de Produ\u00e7\u00e3o e Comercializa\u00e7\u00e3o "
                "da Agricultura Urbana e Familiar Agroecol\u00f3gica"
            ),
            Departamento.Tipo.DIRETORIA,
            sup_san,
        )

        unidade(
            "Ger\u00eancia de Apoio \u00e0 Comercializa\u00e7\u00e3o",
            Departamento.Tipo.GERENCIA,
            dir_producao,
        )

        unidade(
            "Ger\u00eancia de Apoio \u00e0 Produ\u00e7\u00e3o Agroecol\u00f3gica",
            Departamento.Tipo.GERENCIA,
            dir_producao,
        )

        dir_assistencia = unidade(
            "Diretoria de Assist\u00eancia e Educa\u00e7\u00e3o Alimentar",
            Departamento.Tipo.DIRETORIA,
            sup_san,
        )

        unidade(
            (
                "Ger\u00eancia do Banco de Alimentos "
                "e A\u00e7\u00f5es Emergenciais"
            ),
            Departamento.Tipo.GERENCIA,
            dir_assistencia,
        )

        unidade(
            (
                "Ger\u00eancia de Restaurantes Populares "
                "e Cozinhas Comunit\u00e1rias"
            ),
            Departamento.Tipo.GERENCIA,
            dir_assistencia,
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Carga concluida. Criados: {criados}. "
                f"Ja existentes/ajustados: "
                f"{atualizados_ou_existentes}."
            )
        )
