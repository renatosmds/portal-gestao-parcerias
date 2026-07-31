from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("empresas", "0013_alter_empresa_termos"),
        ("prestacao", "0008_remove_prestacao_departamentos"),
    ]

    operations = [
        migrations.AlterField(
            model_name="empresa",
            name="prestacao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="empresas_legadas",
                related_query_name="empresa_legada",
                to="prestacao.prestacao",
                verbose_name="Prestação legada",
            ),
        ),
    ]
