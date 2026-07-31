from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):
    initial = True
    dependencies = [("prestacao", "0011_alter_historicoprestacao_options_and_more"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="MetaExecucao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(blank=True, max_length=30)),
                ("titulo", models.CharField(max_length=180)),
                ("descricao", models.TextField(blank=True)),
                ("unidade", models.CharField(choices=[("numero", "Número"), ("percentual", "Percentual"), ("moeda", "Valor em reais"), ("pessoas", "Pessoas atendidas"), ("horas", "Horas")], default="numero", max_length=20)),
                ("valor_previsto", models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0"))])),
                ("valor_realizado", models.DecimalField(decimal_places=2, default=0, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0"))])),
                ("inicio", models.DateField(blank=True, null=True)), ("fim", models.DateField(blank=True, null=True)),
                ("situacao", models.CharField(choices=[("nao_iniciada", "Não iniciada"), ("em_andamento", "Em andamento"), ("atingida", "Atingida"), ("parcial", "Parcialmente atingida"), ("nao_atingida", "Não atingida"), ("suspensa", "Suspensa")], default="nao_iniciada", max_length=24)),
                ("justificativa", models.TextField(blank=True)), ("responsavel", models.CharField(blank=True, max_length=150)),
                ("criado_em", models.DateTimeField(auto_now_add=True)), ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("atualizado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="metas_atualizadas", to=settings.AUTH_USER_MODEL)),
                ("criado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="metas_criadas", to=settings.AUTH_USER_MODEL)),
                ("prestacao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="metas_execucao", to="prestacao.prestacao")),
            ], options={"ordering": ["prestacao", "codigo", "titulo"]}),
        migrations.CreateModel(
            name="AtualizacaoMeta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("valor_realizado", models.DecimalField(decimal_places=2, max_digits=14)),
                ("situacao", models.CharField(choices=[("nao_iniciada", "Não iniciada"), ("em_andamento", "Em andamento"), ("atingida", "Atingida"), ("parcial", "Parcialmente atingida"), ("nao_atingida", "Não atingida"), ("suspensa", "Suspensa")], max_length=24)),
                ("observacao", models.TextField(blank=True)), ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("meta", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="atualizacoes", to="metas.metaexecucao")),
                ("usuario", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ], options={"ordering": ["-criado_em"]}),
    ]
