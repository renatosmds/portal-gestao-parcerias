from django.db import migrations


def inicializar(apps, schema_editor):
    Sequencia = apps.get_model(
        "core",
        "SequenciaPseudonimo",
    )

    Funcionario = apps.get_model(
        "funcionarios",
        "Funcionario",
    )

    Fornecedor = apps.get_model(
        "fornecedores",
        "Fornecedores",
    )

    funcionarios = list(
        Funcionario.objects
        .order_by("pk")
        .values_list("pk", flat=True)
    )

    fornecedores = list(
        Fornecedor.objects
        .order_by("pk")
        .values_list("pk", flat=True)
    )

    # Fase temporaria para evitar conflitos
    # com campos unique durante a renumeracao.
    for numero, pk in enumerate(
        funcionarios,
        1,
    ):
        Funcionario.objects.filter(
            pk=pk
        ).update(
            codigo_pseudonimo=(
                f"TMP-{numero:06d}"
            )
        )

    for numero, pk in enumerate(
        fornecedores,
        1,
    ):
        Fornecedor.objects.filter(
            pk=pk
        ).update(
            codigo_pseudonimo=(
                f"TMP-{numero:06d}"
            )
        )

    # Codigos definitivos.
    for numero, pk in enumerate(
        funcionarios,
        1,
    ):
        Funcionario.objects.filter(
            pk=pk
        ).update(
            codigo_pseudonimo=(
                f"COL-{numero:06d}"
            )
        )

    for numero, pk in enumerate(
        fornecedores,
        1,
    ):
        Fornecedor.objects.filter(
            pk=pk
        ).update(
            codigo_pseudonimo=(
                f"FOR-{numero:06d}"
            )
        )

    Sequencia.objects.update_or_create(
        tipo="COL",
        defaults={
            "ultimo_numero": len(funcionarios),
        },
    )

    Sequencia.objects.update_or_create(
        tipo="FOR",
        defaults={
            "ultimo_numero": len(fornecedores),
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "core",
            "0003_sequenciapseudonimo",
        ),
        (
            "funcionarios",
            "0028_alter_funcionario_user",
        ),
        (
            "fornecedores",
            "0006_preencher_codigos_pseudonimos",
        ),
    ]

    operations = [
        migrations.RunPython(
            inicializar,
            migrations.RunPython.noop,
        ),
    ]
