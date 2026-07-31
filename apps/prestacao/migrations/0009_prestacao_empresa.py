from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("empresas", "0014_alter_empresa_prestacao"),
        ("prestacao", "0008_remove_prestacao_departamentos"),
    ]

    operations = [
        migrations.AddField(
            model_name="prestacao",
            name="empresa",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="prestacoes_vinculadas",
                related_query_name="prestacao_vinculada",
                to="empresas.empresa",
                verbose_name="Empresa",
            ),
        ),
        migrations.AlterField(
            model_name="prestacao",
            name="imagem",
            field=models.ImageField(blank=True, null=True, upload_to=""),
        ),
        migrations.AlterModelOptions(
            name="prestacao",
            options={
                "ordering": ["numtermo", "tipoTermo"],
                "verbose_name": "Prestação de contas",
                "verbose_name_plural": "Prestações de contas",
            },
        ),
    ]
