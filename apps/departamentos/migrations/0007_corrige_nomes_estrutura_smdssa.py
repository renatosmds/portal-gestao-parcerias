from django.db import migrations
from django.db.models import Q


def corrigir_estrutura(apps, schema_editor):
    Empresa = apps.get_model("empresas", "Empresa")
    Departamento = apps.get_model(
        "departamentos",
        "Departamento",
    )

    empresa = (
        Empresa.objects
        .filter(nome__icontains="Contagem")
        .order_by("pk")
        .first()
    )

    if not empresa:
        return

    secretaria = (
        Departamento.objects
        .filter(
            empresa=empresa,
            nome__icontains="Desenvolvimento Social",
        )
        .filter(
            nome__icontains="Seguran",
        )
        .order_by("pk")
        .first()
    )

    if not secretaria:
        return

    def nome_corrompido(nome):
        return "".join(
            caractere
            if ord(caractere) < 128
            else "?"
            for caractere in nome
        )

    def unidade(nome, tipo, superior):
        nome_ruim = nome_corrompido(nome)

        obj = (
            Departamento.objects
            .filter(
                empresa=empresa,
                superior=superior,
                tipo=tipo,
            )
            .filter(
                Q(nome__iexact=nome)
                | Q(nome__iexact=nome_ruim)
            )
            .order_by("pk")
            .first()
        )

        if not obj:
            obj = (
                Departamento.objects
                .filter(
                    empresa=empresa,
                )
                .filter(
                    Q(nome__iexact=nome)
                    | Q(nome__iexact=nome_ruim)
                )
                .order_by("pk")
                .first()
            )

        if obj:
            campos = []

            if obj.nome != nome:
                obj.nome = nome
                campos.append("nome")

            if obj.tipo != tipo:
                obj.tipo = tipo
                campos.append("tipo")

            if obj.superior_id != superior.pk:
                obj.superior = superior
                campos.append("superior")

            if campos:
                obj.save(update_fields=campos)

            return obj

        return Departamento.objects.create(
            empresa=empresa,
            nome=nome,
            tipo=tipo,
            superior=superior,
        )

    unidade(
        "Gabinete do Secret\u00e1rio",
        "gabinete",
        secretaria,
    )

    unidade(
        "Assessoria de Gest\u00e3o e Inova\u00e7\u00e3o",
        "assessoria",
        secretaria,
    )

    sup_operacao = unidade(
        "Superintend\u00eancia de Opera\u00e7\u00e3o Institucional",
        "superintendencia",
        secretaria,
    )

    dir_processos = unidade(
        "Diretoria de Processos Operacionais",
        "diretoria",
        sup_operacao,
    )

    unidade(
        "Ger\u00eancia de Apoio a Compras e Licita\u00e7\u00e3o",
        "gerencia",
        dir_processos,
    )

    unidade(
        "Ger\u00eancia de Patrim\u00f4nio e Manuten\u00e7\u00e3o",
        "gerencia",
        dir_processos,
    )

    unidade(
        (
            "Ger\u00eancia de Gest\u00e3o de Pessoas "
            "e Apoio Log\u00edstico"
        ),
        "gerencia",
        dir_processos,
    )

    unidade(
        "Diretoria de Or\u00e7amento e Finan\u00e7as",
        "diretoria",
        sup_operacao,
    )

    sup_parcerias = unidade(
        "Superintend\u00eancia de Parcerias",
        "superintendencia",
        secretaria,
    )

    dir_parcerias = unidade(
        (
            "Diretoria de Parceira e "
            "Presta\u00e7\u00e3o de Contas"
        ),
        "diretoria",
        sup_parcerias,
    )

    unidade(
        "Ger\u00eancia de Conv\u00eanios",
        "gerencia",
        dir_parcerias,
    )

    unidade(
        "Ger\u00eancia de Presta\u00e7\u00e3o de Contas",
        "gerencia",
        dir_parcerias,
    )

    sub_assistencia = unidade(
        "Subsecretaria de Assist\u00eancia Social",
        "subsecretaria",
        secretaria,
    )

    sup_assistencia = unidade(
        "Superintend\u00eancia de Assist\u00eancia Social",
        "superintendencia",
        sub_assistencia,
    )

    dir_programas = unidade(
        "Diretoria de Programas e Benef\u00edcio",
        "diretoria",
        sup_assistencia,
    )

    unidade(
        "Ger\u00eancia de Cadastro e Atendimento",
        "gerencia",
        dir_programas,
    )

    unidade(
        "Diretoria de Prote\u00e7\u00e3o Social B\u00e1sica",
        "diretoria",
        sup_assistencia,
    )

    unidade(
        (
            "Diretoria de Prote\u00e7\u00e3o Social Especial "
            "de M\u00e9dia Complexidade"
        ),
        "diretoria",
        sup_assistencia,
    )

    unidade(
        (
            "Diretoria de Prote\u00e7\u00e3o Social Especial "
            "de Alta Complexidade"
        ),
        "diretoria",
        sup_assistencia,
    )

    dir_suas = unidade(
        (
            "Diretoria de Gest\u00e3o do Sistema \u00danico "
            "da Assist\u00eancia Social \u2013 SUAS"
        ),
        "diretoria",
        sup_assistencia,
    )

    unidade(
        (
            "Ger\u00eancia de Gest\u00e3o de Trabalho "
            "e Educa\u00e7\u00e3o Permanente"
        ),
        "gerencia",
        dir_suas,
    )

    unidade(
        "Ger\u00eancia da Vigil\u00e2ncia Socioassistencial",
        "gerencia",
        dir_suas,
    )

    unidade(
        "Ger\u00eancia de Regulamenta\u00e7\u00e3o do SUAS",
        "gerencia",
        dir_suas,
    )

    sub_alimentar = unidade(
        (
            "Subsecretaria de Seguran\u00e7a Alimentar, "
            "Nutricional e Agroecologia"
        ),
        "subsecretaria",
        secretaria,
    )

    sup_alimentar = unidade(
        (
            "Superintend\u00eancia de Seguran\u00e7a Alimentar, "
            "Nutricional e Agroecologia"
        ),
        "superintendencia",
        sub_alimentar,
    )

    dir_producao = unidade(
        (
            "Diretoria de Produ\u00e7\u00e3o e Comercializa\u00e7\u00e3o "
            "da Agricultura Urbana e Familiar Agroecol\u00f3gica"
        ),
        "diretoria",
        sup_alimentar,
    )

    unidade(
        "Ger\u00eancia de Apoio \u00e0 Comercializa\u00e7\u00e3o",
        "gerencia",
        dir_producao,
    )

    unidade(
        "Ger\u00eancia de Apoio \u00e0 Produ\u00e7\u00e3o Agroecol\u00f3gica",
        "gerencia",
        dir_producao,
    )

    dir_assistencia_alimentar = unidade(
        (
            "Diretoria de Assist\u00eancia "
            "e Educa\u00e7\u00e3o Alimentar"
        ),
        "diretoria",
        sup_alimentar,
    )

    unidade(
        (
            "Ger\u00eancia do Banco de Alimentos "
            "e A\u00e7\u00f5es Emergenciais"
        ),
        "gerencia",
        dir_assistencia_alimentar,
    )

    unidade(
        (
            "Ger\u00eancia de Restaurantes Populares "
            "e Cozinhas Comunit\u00e1rias"
        ),
        "gerencia",
        dir_assistencia_alimentar,
    )


def reverso(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "departamentos",
            "0006_corrige_carga_estrutura_smdssa",
        ),
    ]

    operations = [
        migrations.RunPython(
            corrigir_estrutura,
            reverso,
        ),
    ]
