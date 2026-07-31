from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("documentos", "0009_auto_20210201_1657"),
        ("empresas", "0014_alter_empresa_prestacao"),
        ("lancamentos", "0001_initial"),
        ("prestacao", "0009_prestacao_empresa"),
        ("termos", "0017_alter_termos_extratosbancarios_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="documento",
            options={
                "ordering": ["status", "-atualizado_em", "-id"],
                "verbose_name": "Documento",
                "verbose_name_plural": "Documentos",
            },
        ),
        migrations.AlterField(
            model_name="documento",
            name="descricao",
            field=models.CharField(
                max_length=150,
                verbose_name="Descrição",
            ),
        ),
        migrations.AlterField(
            model_name="documento",
            name="arquivo",
            field=models.FileField(
                upload_to="documentos/%Y/%m/",
                verbose_name="Arquivo",
            ),
        ),
        migrations.AlterField(
            model_name="documento",
            name="pertence",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="documentos_legados",
                to="funcionarios.funcionario",
                verbose_name="Funcionário (legado)",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="empresa",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="documentos",
                related_query_name="documento",
                to="empresas.empresa",
                verbose_name="Empresa",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="termo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="documentos_vinculados",
                related_query_name="documento_vinculado",
                to="termos.termos",
                verbose_name="Termo",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="prestacao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="documentos_vinculados",
                related_query_name="documento_vinculado",
                to="prestacao.prestacao",
                verbose_name="Prestação de contas",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="lancamento",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="documentos_vinculados",
                related_query_name="documento_vinculado",
                to="lancamentos.lancamento",
                verbose_name="Lançamento",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="conferido_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="documentos_conferidos",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Conferido por",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("nota_fiscal", "Nota fiscal"),
                    ("comprovante", "Comprovante de pagamento"),
                    ("atesto", "Atesto"),
                    ("extrato", "Extrato bancário"),
                    ("contrato", "Contrato / termo"),
                    ("folha", "Folha de pagamento"),
                    ("guia", "Guia de recolhimento"),
                    ("outro", "Outro"),
                ],
                default="outro",
                max_length=30,
                verbose_name="Tipo de documento",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="status",
            field=models.CharField(
                choices=[
                    ("pendente", "Pendente"),
                    ("em_conferencia", "Em conferência"),
                    ("conferido", "Conferido"),
                    ("com_pendencia", "Com pendência"),
                    ("reprovado", "Reprovado"),
                ],
                default="pendente",
                max_length=30,
                verbose_name="Status da conferência",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="numero_documento",
            field=models.CharField(
                blank=True,
                max_length=80,
                verbose_name="Número do documento",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="data_documento",
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name="Data do documento",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="documento_legivel",
            field=models.BooleanField(
                default=False,
                verbose_name="Documento legível",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="dados_compativeis",
            field=models.BooleanField(
                default=False,
                verbose_name="Dados compatíveis",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="vigencia_valida",
            field=models.BooleanField(
                default=False,
                verbose_name="Vigência válida",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="pagamento_comprovado",
            field=models.BooleanField(
                default=False,
                verbose_name="Pagamento comprovado",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="atesto_valido",
            field=models.BooleanField(
                default=False,
                verbose_name="Atesto válido",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="observacoes",
            field=models.TextField(
                blank=True,
                verbose_name="Observações da conferência",
            ),
        ),
        migrations.AddField(
            model_name="documento",
            name="criado_em",
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="documento",
            name="atualizado_em",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="documento",
            name="conferido_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
