from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "funcionarios",
            "0034_migra_cargo_nivel_equipamento",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="funcionario",
            name="cargo",
        ),
        migrations.RemoveField(
            model_name="funcionario",
            name="nivel",
        ),
        migrations.RemoveField(
            model_name="funcionario",
            name="equipamento",
        ),
        migrations.RenameField(
            model_name="funcionario",
            old_name="cargo_cadastro",
            new_name="cargo",
        ),
        migrations.RenameField(
            model_name="funcionario",
            old_name="nivel_cadastro",
            new_name="nivel",
        ),
        migrations.RenameField(
            model_name="funcionario",
            old_name="equipamento_cadastro",
            new_name="equipamento",
        ),
    ]
