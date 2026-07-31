from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("empresas", "0012_alter_empresa_parcerias"),
        ("termos", "0015_termos_analista_termos_apelido_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="termos",
            name="empresa",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="termos_vinculados",
                related_query_name="termo_vinculado",
                to="empresas.empresa",
                verbose_name="Empresa",
            ),
        ),
        migrations.AlterModelOptions(
            name="termos",
            options={
                "ordering": ["termo", "numtermo"],
                "verbose_name": "Termo",
                "verbose_name_plural": "Termos",
            },
        ),
    ]
