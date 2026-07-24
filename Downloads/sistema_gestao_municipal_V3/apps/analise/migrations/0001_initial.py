from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("empresas", "0014_alter_empresa_prestacao"),
        ("prestacao", "0009_prestacao_empresa"),
        ("termos", "0016_termos_empresa"),
    ]

    operations = [
        migrations.CreateModel(
            name="Analise",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nomeOSC",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        null=True,
                        verbose_name="Nome da OSC",
                    ),
                ),
                (
                    "numRA",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        null=True,
                        verbose_name="Nº Relatório de Auditoria (RA)",
                    ),
                ),
                (
                    "item",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        null=True,
                        verbose_name="Item",
                    ),
                ),
                (
                    "inconformidade",
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name="Inconformidade",
                    ),
                ),
                (
                    "recomendacoes",
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name="Recomendações",
                    ),
                ),
                (
                    "posicaoSecretaria",
                    models.TextField(
                        blank=True,
                        null=True,
                        verbose_name="Posição da Secretaria",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Status",
                    ),
                ),
                (
                    "concluida",
                    models.BooleanField(
                        default=False,
                        verbose_name="Concluída",
                    ),
                ),
                (
                    "criada_em",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Criada em",
                    ),
                ),
                (
                    "atualizada_em",
                    models.DateTimeField(
                        auto_now=True,
                        verbose_name="Atualizada em",
                    ),
                ),
                (
                    "empresa",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="analises_vinculadas",
                        related_query_name="analise_vinculada",
                        to="empresas.empresa",
                        verbose_name="Empresa",
                    ),
                ),
                (
                    "numtermo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="analises_vinculadas",
                        related_query_name="analise_vinculada",
                        to="termos.termos",
                        verbose_name="Termo",
                    ),
                ),
                (
                    "prestacao",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="analises_vinculadas",
                        related_query_name="analise_vinculada",
                        to="prestacao.prestacao",
                        verbose_name="Prestação de contas",
                    ),
                ),
            ],
            options={
                "verbose_name": "Análise",
                "verbose_name_plural": "Análises",
                "ordering": [
                    "concluida",
                    "numtermo__termo",
                    "numRA",
                    "item",
                ],
            },
        ),
    ]
