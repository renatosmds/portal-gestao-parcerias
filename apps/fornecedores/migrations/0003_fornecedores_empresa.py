from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("empresas", "0011_empresa_curso"),
        ("fornecedores", "0002_auto_20210124_1807"),
    ]

    operations = [
        migrations.AddField(
            model_name="fornecedores",
            name="empresa",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fornecedores",
                to="empresas.empresa",
            ),
        ),
        migrations.AlterModelOptions(
            name="fornecedores",
            options={
                "ordering": ["credor"],
                "verbose_name": "Fornecedor",
                "verbose_name_plural": "Fornecedores",
            },
        ),
    ]
