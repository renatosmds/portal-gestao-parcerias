from django.db import migrations


def preencher_codigos(apps, schema_editor):
    Funcionario = apps.get_model(
        "funcionarios",
        "Funcionario",
    )

    for obj in Funcionario.objects.filter(
        codigo_pseudonimo__isnull=True
    ).iterator():
        obj.codigo_pseudonimo = (
            f"COL-{obj.pk:06d}"
        )

        obj.save(
            update_fields=[
                "codigo_pseudonimo",
            ]
        )


def reverter_codigos(apps, schema_editor):
    Funcionario = apps.get_model(
        "funcionarios",
        "Funcionario",
    )

    Funcionario.objects.update(
        codigo_pseudonimo=None
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "funcionarios",
            "0026_funcionario_codigo_pseudonimo",
        ),
    ]

    operations = [
        migrations.RunPython(
            preencher_codigos,
            reverter_codigos,
        ),
    ]
