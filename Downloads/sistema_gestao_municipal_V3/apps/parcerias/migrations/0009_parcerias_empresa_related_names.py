from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("empresas", "0011_empresa_curso"),
        ("fornecedores", "0003_fornecedores_empresa"),
        ("termos", "0001_initial"),
        ("parcerias", "0008_remove_parcerias_departamento"),
    ]

    operations = [
        migrations.AddField(
            model_name="parcerias",
            name="empresa",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="parcerias_vinculadas",
                to="empresas.empresa",
                verbose_name="Empresa",
            ),
        ),
        migrations.AlterField(
            model_name="parcerias",
            name="credor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="parcerias_vinculadas",
                to="fornecedores.fornecedores",
                verbose_name="Fornecedor/credor",
            ),
        ),
        migrations.AlterField(
            model_name="parcerias",
            name="numtermo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="parcerias_vinculadas",
                to="termos.termos",
                verbose_name="Termo",
            ),
        ),
        migrations.AlterModelOptions(
            name="parcerias",
            options={
                "ordering": ["numtermo__termo", "nomeOSC"],
                "verbose_name": "Parceria",
                "verbose_name_plural": "Parcerias",
            },
        ),
        migrations.AlterField(
            model_name="parcerias",
            name="nomeOSC",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name="OSC",
            ),
        ),
    ]
