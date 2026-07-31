from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("analise", "0001_initial"),
        ("empresas", "0014_alter_empresa_prestacao"),
        ("fornecedores", "0003_fornecedores_empresa"),
        ("prestacao", "0009_prestacao_empresa"),
        ("termos", "0017_alter_termos_extratosbancarios_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lancamento",
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
                    "numero_lancamento",
                    models.CharField(
                        max_length=30,
                        verbose_name="Nº do lançamento",
                    ),
                ),
                (
                    "tipo_documento",
                    models.CharField(
                        choices=[
                            ("nfe", "NF-e"),
                            ("nfce", "NFC-e"),
                            ("nfse", "NFS-e"),
                            ("recibo", "Recibo"),
                            ("boleto", "Boleto"),
                            ("folha", "Folha de pagamento"),
                            ("outro", "Outro"),
                        ],
                        default="nfe",
                        max_length=20,
                        verbose_name="Tipo de documento",
                    ),
                ),
                (
                    "numero_documento",
                    models.CharField(
                        blank=True,
                        max_length=80,
                        verbose_name="Nº do documento fiscal",
                    ),
                ),
                (
                    "chave_acesso",
                    models.CharField(
                        blank=True,
                        max_length=60,
                        verbose_name="Chave de acesso",
                    ),
                ),
                (
                    "data_documento",
                    models.DateField(verbose_name="Data do documento"),
                ),
                (
                    "data_pagamento",
                    models.DateField(
                        blank=True,
                        null=True,
                        verbose_name="Data do pagamento",
                    ),
                ),
                (
                    "descricao",
                    models.CharField(
                        max_length=255,
                        verbose_name="Descrição da despesa",
                    ),
                ),
                (
                    "valor_documento",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=15,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0.00")
                            )
                        ],
                        verbose_name="Valor do documento",
                    ),
                ),
                (
                    "valor_glosa",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=15,
                        validators=[
                            django.core.validators.MinValueValidator(
                                Decimal("0.00")
                            )
                        ],
                        verbose_name="Valor da glosa",
                    ),
                ),
                (
                    "situacao",
                    models.CharField(
                        choices=[
                            ("nao_analisado", "Não analisado"),
                            ("regular", "Regular"),
                            ("ressalva", "Aprovado com ressalva"),
                            ("reprovado", "Reprovado"),
                            ("glosado", "Glosado"),
                        ],
                        default="nao_analisado",
                        max_length=20,
                        verbose_name="Situação",
                    ),
                ),
                (
                    "atestado",
                    models.BooleanField(
                        default=False,
                        verbose_name="Documento atestado",
                    ),
                ),
                (
                    "justificativa",
                    models.TextField(
                        blank=True,
                        verbose_name="Justificativa / inconformidade",
                    ),
                ),
                (
                    "recomendacao",
                    models.TextField(
                        blank=True,
                        verbose_name="Recomendação",
                    ),
                ),
                (
                    "documento",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="lancamentos/documentos/%Y/%m/",
                        verbose_name="Documento comprobatório",
                    ),
                ),
                (
                    "comprovante_pagamento",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="lancamentos/pagamentos/%Y/%m/",
                        verbose_name="Comprovante de pagamento",
                    ),
                ),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                (
                    "analise",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lancamentos",
                        related_query_name="lancamento",
                        to="analise.analise",
                        verbose_name="Análise técnica",
                    ),
                ),
                (
                    "criado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lancamentos_criados",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Criado por",
                    ),
                ),
                (
                    "empresa",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lancamentos",
                        related_query_name="lancamento",
                        to="empresas.empresa",
                        verbose_name="Empresa",
                    ),
                ),
                (
                    "fornecedor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lancamentos",
                        related_query_name="lancamento",
                        to="fornecedores.fornecedores",
                        verbose_name="Fornecedor",
                    ),
                ),
                (
                    "prestacao",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lancamentos",
                        related_query_name="lancamento",
                        to="prestacao.prestacao",
                        verbose_name="Prestação de contas",
                    ),
                ),
                (
                    "termo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lancamentos",
                        related_query_name="lancamento",
                        to="termos.termos",
                        verbose_name="Termo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lançamento",
                "verbose_name_plural": "Lançamentos",
                "ordering": ["-data_documento", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="lancamento",
            constraint=models.UniqueConstraint(
                fields=("empresa", "numero_lancamento"),
                name="lancamento_unico_por_empresa",
            ),
        ),
    ]
