from django.db import migrations


def preencher_codigos(apps, schema_editor):
    Fornecedor = apps.get_model(
        "fornecedores",
        "Fornecedores",
    )

    for obj in Fornecedor.objects.filter(
        codigo_pseudonimo__isnull=True
    ).iterator():
        obj.codigo_pseudonimo = (
            f"FOR-{obj.pk:06d}"
        )

        obj.save(
            update_fields=[
                "codigo_pseudonimo",
            ]
        )


def reverter_codigos(apps, schema_editor):
    Fornecedor = apps.get_model(
        "fornecedores",
        "Fornecedores",
    )

    Fornecedor.objects.update(
        codigo_pseudonimo=None
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "fornecedores",
            "0005_fornecedores_codigo_pseudonimo",
        ),
    ]

    operations = [
        migrations.RunPython(
            preencher_codigos,
            reverter_codigos,
        ),
    ]
