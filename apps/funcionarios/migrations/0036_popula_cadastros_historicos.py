from django.db import migrations


CARGOS = [
    "Administrador(a)",
    "Administrador(a) do Sistema",
    "Almoxarife",
    "Analista de Comunica??o",
    "Analista de Processos",
    "Assistente Administrativo",
    "Assistente de RH",
    "Atendente de Restaurante",
    "Auxiliar de Coordena??o",
    "Auxiliar de Cozinha",
    "Auxiliar de Escrit?rio",
    "Auxiliar de Servi?os Gerais",
    "Caixa",
    "Chefe de Cozinha",
    "Comissionado(a)",
    "Contratado(a)",
    "Coordenador(a)",
    "Coordenador(a) Administrativo Financeiro",
    "Coordenador(a) de Eventos",
    "Coordenador(a) de log?stica",
    "Coordenador(a) de Projetos",
    "Cozinheiro(a)",
    "Diretor(a) de Abastecimento",
    "Efetivo(a)",
    "Encarregado(a) de Manuten??o",
    "Gerente Administrativo",
    "Gerente Administrativo Financeiro",
    "Gerente de Presta??o de Contas",
    "Gerente de Qualidade",
    "Gerente Financeiro",
    "Gestor(a)",
    "Motorista",
    "Nutricionista",
    "Operador(a) de Manuten??o",
    "Pol?tico",
    "Saladeira(o)",
    "Supervisor(a) de Manuten??o",
    "Supervisor(a) de Servi?os Gerais",
    "T?cnico de Contabilidade",
]


NIVEIS = [
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
] + [
    f"DAM {numero:02d}"
    for numero in range(1, 21)
]


EQUIPAMENTOS = [
    "Cozinha Comunit?ria Nacional",
    "Cozinha Comunit?ria Nova Contagem",
    "Restaurante Popular Eldorado",
    "Restaurante Popular Nova Contagem",
    "Restaurante Popular Ressaca",
]


def normalizar_registro(
    Modelo,
    Funcionario,
    empresa,
    campo_funcionario,
    nome_final,
    ordem=None,
):
    existentes = list(
        Modelo.objects.filter(
            empresa_id=empresa.pk,
        )
    )

    destino = None

    for obj in existentes:
        if obj.nome.casefold() == nome_final.casefold():
            destino = obj
            break

    if destino is None:
        kwargs = {
            "empresa_id": empresa.pk,
            "nome": nome_final,
            "descricao": "",
            "ativo": True,
        }

        if ordem is not None:
            kwargs["ordem"] = ordem

        destino = Modelo.objects.create(**kwargs)

    else:
        alterados = []

        if destino.nome != nome_final:
            destino.nome = nome_final
            alterados.append("nome")

        if not destino.ativo:
            destino.ativo = True
            alterados.append("ativo")

        if ordem is not None and destino.ordem != ordem:
            destino.ordem = ordem
            alterados.append("ordem")

        if alterados:
            destino.save(update_fields=alterados)

    # Corrige eventuais registros antigos com a mesma descricao,
    # mas grafia/caixa diferente.
    for antigo in existentes:
        if antigo.pk == destino.pk:
            continue

        if antigo.nome.casefold() == nome_final.casefold():
            Funcionario.objects.filter(
                empresa_id=empresa.pk,
                **{f"{campo_funcionario}_id": antigo.pk},
            ).update(
                **{f"{campo_funcionario}_id": destino.pk}
            )

            antigo.delete()

    return destino


def popular(apps, schema_editor):
    Empresa = apps.get_model("empresas", "Empresa")
    Funcionario = apps.get_model(
        "funcionarios",
        "Funcionario",
    )
    Cargo = apps.get_model("funcionarios", "Cargo")
    Nivel = apps.get_model("funcionarios", "Nivel")
    Equipamento = apps.get_model(
        "funcionarios",
        "Equipamento",
    )

    for empresa in Empresa.objects.all().iterator():

        for nome in CARGOS:
            normalizar_registro(
                Cargo,
                Funcionario,
                empresa,
                "cargo",
                nome,
            )

        for ordem, nome in enumerate(
            NIVEIS,
            start=1,
        ):
            normalizar_registro(
                Nivel,
                Funcionario,
                empresa,
                "nivel",
                nome,
                ordem=ordem,
            )

        for nome in EQUIPAMENTOS:
            normalizar_registro(
                Equipamento,
                Funcionario,
                empresa,
                "equipamento",
                nome,
            )


class Migration(migrations.Migration):

    dependencies = [
        (
            "funcionarios",
            "0035_finaliza_cadastros_colaborador",
        ),
    ]

    operations = [
        migrations.RunPython(
            popular,
            migrations.RunPython.noop,
        ),
    ]
