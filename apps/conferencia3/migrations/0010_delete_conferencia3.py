from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "conferencia3",
            "0009_remove_conferencia3_departamento_and_more",
        ),
        (
            "empresas",
            "0016_remove_empresa_conferencia3",
        ),
        (
            "funcionarios",
            "0025_remove_funcionario_conferencia3",
        ),
    ]

    operations = [
        migrations.DeleteModel(
            name="Conferencia3",
        ),
    ]
