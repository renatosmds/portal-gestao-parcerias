from django.db import migrations


def carregar_estrutura(apps, schema_editor):
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

    alterado = False

    if secretaria.tipo != "departamento":
        secretaria.tipo = "departamento"
        alterado = True

    if secretaria.superior_id is not None:
        secretaria.superior = None
        alterado = True

    if alterado:
        secretaria.save(
            update_fields=[
                "tipo",
                "superior",
            ]
        )

    def unidade(nome, tipo, superior):
        obj = (
            Departamento.objects
            .filter(
                empresa=empresa,
                nome__iexact=nome,
            )
            .first()
        )

        if obj:
            campos = []

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
        "Gabinete do Secret?rio",
        "gabinete",
        secretaria,
    )

    unidade(
        "Assessoria de Gest?o e Inova??o",
        "assessoria",
        secretaria,
    )

    sup_operacao = unidade(
        "Superintend?ncia de Opera??o Institucional",
        "superintendencia",
        secretaria,
    )

    dir_processos = unidade(
        "Diretoria de Processos Operacionais",
        "diretoria",
        sup_operacao,
    )

    unidade(
        "Ger?ncia de Apoio a Compras e Licita??o",
        "gerencia",
        dir_processos,
    )

    unidade(
        "Ger?ncia de Patrim?nio e Manuten??o",
        "gerencia",
        dir_processos,
    )

    unidade(
        "Ger?ncia de Gest?o de Pessoas e Apoio Log?stico",
        "gerencia",
        dir_processos,
    )

    unidade(
        "Diretoria de Or?amento e Finan?as",
        "diretoria",
        sup_operacao,
    )

    sup_parcerias = unidade(
        "Superintend?ncia de Parcerias",
        "superintendencia",
        secretaria,
    )

    dir_parcerias = unidade(
        "Diretoria de Parceira e Presta??o de Contas",
        "diretoria",
        sup_parcerias,
    )

    unidade(
        "Ger?ncia de Conv?nios",
        "gerencia",
        dir_parcerias,
    )

    unidade(
        "Ger?ncia de Presta??o de Contas",
        "gerencia",
        dir_parcerias,
    )

    sub_assistencia = unidade(
        "Subsecretaria de Assist?ncia Social",
        "subsecretaria",
        secretaria,
    )

    sup_assistencia = unidade(
        "Superintend?ncia de Assist?ncia Social",
        "superintendencia",
        sub_assistencia,
    )

    dir_programas = unidade(
        "Diretoria de Programas e Benef?cio",
        "diretoria",
        sup_assistencia,
    )

    unidade(
        "Ger?ncia de Cadastro e Atendimento",
        "gerencia",
        dir_programas,
    )

    unidade(
        "Diretoria de Prote??o Social B?sica",
        "diretoria",
        sup_assistencia,
    )

    unidade(
        (
            "Diretoria de Prote??o Social Especial "
            "de M?dia Complexidade"
        ),
        "diretoria",
        sup_assistencia,
    )

    unidade(
        (
            "Diretoria de Prote??o Social Especial "
            "de Alta Complexidade"
        ),
        "diretoria",
        sup_assistencia,
    )

    dir_suas = unidade(
        (
            "Diretoria de Gest?o do Sistema ?nico "
            "da Assist?ncia Social ? SUAS"
        ),
        "diretoria",
        sup_assistencia,
    )

    unidade(
        (
            "Ger?ncia de Gest?o de Trabalho "
            "e Educa??o Permanente"
        ),
        "gerencia",
        dir_suas,
    )

    unidade(
        "Ger?ncia da Vigil?ncia Socioassistencial",
        "gerencia",
        dir_suas,
    )

    unidade(
        "Ger?ncia de Regulamenta??o do SUAS",
        "gerencia",
        dir_suas,
    )

    sub_alimentar = unidade(
        (
            "Subsecretaria de Seguran?a Alimentar, "
            "Nutricional e Agroecologia"
        ),
        "subsecretaria",
        secretaria,
    )

    sup_alimentar = unidade(
        (
            "Superintend?ncia de Seguran?a Alimentar, "
            "Nutricional e Agroecologia"
        ),
        "superintendencia",
        sub_alimentar,
    )

    dir_producao = unidade(
        (
            "Diretoria de Produ??o e Comercializa??o "
            "da Agricultura Urbana e Familiar Agroecol?gica"
        ),
        "diretoria",
        sup_alimentar,
    )

    unidade(
        "Ger?ncia de Apoio ? Comercializa??o",
        "gerencia",
        dir_producao,
    )

    unidade(
        "Ger?ncia de Apoio ? Produ??o Agroecol?gica",
        "gerencia",
        dir_producao,
    )

    dir_assistencia_alimentar = unidade(
        "Diretoria de Assist?ncia e Educa??o Alimentar",
        "diretoria",
        sup_alimentar,
    )

    unidade(
        (
            "Ger?ncia do Banco de Alimentos "
            "e A??es Emergenciais"
        ),
        "gerencia",
        dir_assistencia_alimentar,
    )

    unidade(
        (
            "Ger?ncia de Restaurantes Populares "
            "e Cozinhas Comunit?rias"
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
            "0005_carrega_estrutura_smdssa",
        ),
    ]

    operations = [
        migrations.RunPython(
            carregar_estrutura,
            reverso,
        ),
    ]
