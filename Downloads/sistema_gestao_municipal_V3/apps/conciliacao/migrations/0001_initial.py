# Generated for Sprint 25
from decimal import Decimal
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("prestacao", "0011_alter_historicoprestacao_options_and_more"),
        ("lancamentos", "0002_glosas_sprint16"),
    ]
    operations = [
        migrations.CreateModel(
            name="Conciliacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("saldo_inicial", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=15)),
                ("saldo_final_informado", models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ("situacao", models.CharField(choices=[("incompleta", "Conciliação incompleta"), ("com_diferenca", "Conciliação com diferença"), ("fechada", "Conciliação fechada")], default="incompleta", max_length=20)),
                ("observacoes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("criado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="conciliacoes_criadas", to=settings.AUTH_USER_MODEL)),
                ("prestacao", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="conciliacao_bancaria", to="prestacao.prestacao", verbose_name="Prestação de contas")),
            ],
            options={"verbose_name": "Conciliação bancária", "verbose_name_plural": "Conciliações bancárias", "ordering": ["-atualizado_em"]},
        ),
        migrations.CreateModel(
            name="ImportacaoExtrato",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("arquivo", models.FileField(upload_to="conciliacao/extratos/%Y/%m/")),
                ("formato", models.CharField(max_length=10)),
                ("total_linhas", models.PositiveIntegerField(default=0)),
                ("total_importadas", models.PositiveIntegerField(default=0)),
                ("total_erros", models.PositiveIntegerField(default=0)),
                ("erros", models.JSONField(blank=True, default=list)),
                ("situacao", models.CharField(choices=[("processada", "Processada"), ("com_erros", "Processada com erros")], default="processada", max_length=20)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("conciliacao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="importacoes", to="conciliacao.conciliacao")),
                ("criado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ], options={"ordering": ["-criado_em"]},
        ),
        migrations.CreateModel(
            name="Movimentacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.DateField()),
                ("descricao", models.CharField(max_length=255)),
                ("documento", models.CharField(blank=True, max_length=80)),
                ("favorecido", models.CharField(blank=True, max_length=180)),
                ("tipo", models.CharField(choices=[("credito", "Crédito"), ("debito", "Débito")], max_length=10)),
                ("categoria", models.CharField(choices=[("repasse", "Repasse"), ("rendimento", "Rendimento"), ("estorno", "Estorno"), ("pagamento", "Pagamento"), ("tarifa", "Tarifa bancária"), ("devolucao", "Devolução"), ("transferencia", "Transferência"), ("outro", "Outro")], default="outro", max_length=20)),
                ("valor", models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("saldo_apos", models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ("situacao", models.CharField(choices=[("pendente", "Não conciliada"), ("parcial", "Parcialmente conciliada"), ("conciliada", "Conciliada"), ("ignorada", "Ignorada com justificativa"), ("divergencia", "Com divergência")], default="pendente", max_length=20)),
                ("justificativa", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("conciliacao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="movimentacoes", to="conciliacao.conciliacao")),
                ("importacao", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="movimentacoes", to="conciliacao.importacaoextrato")),
            ], options={"ordering": ["data", "id"]},
        ),
        migrations.AddConstraint(model_name="movimentacao", constraint=models.UniqueConstraint(fields=("conciliacao", "data", "descricao", "valor", "tipo"), name="movimentacao_bancaria_unica")),
        migrations.CreateModel(
            name="VinculoConciliacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("valor", models.DecimalField(decimal_places=2, max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("observacao", models.CharField(blank=True, max_length=255)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("confirmado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("lancamento", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vinculos_bancarios", to="lancamentos.lancamento")),
                ("movimentacao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vinculos", to="conciliacao.movimentacao")),
            ], options={"ordering": ["criado_em"]},
        ),
        migrations.AddConstraint(model_name="vinculoconciliacao", constraint=models.UniqueConstraint(fields=("movimentacao", "lancamento"), name="vinculo_movimentacao_lancamento_unico")),
        migrations.CreateModel(
            name="OcorrenciaConciliacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("mov_sem_lanc", "Movimentação sem lançamento"), ("lanc_sem_mov", "Lançamento sem movimentação"), ("valor_divergente", "Valor divergente"), ("duplicidade", "Possível pagamento em duplicidade"), ("fora_vigencia", "Pagamento fora da vigência"), ("tarifa", "Tarifa bancária"), ("rendimento", "Rendimento não registrado"), ("saldo", "Saldo final divergente"), ("outro", "Outro")], max_length=30)),
                ("descricao", models.TextField()),
                ("situacao", models.CharField(choices=[("pendente", "Pendente"), ("justificada", "Justificada"), ("regularizada", "Regularizada"), ("inconformidade", "Inconformidade"), ("nao_se_aplica", "Não se aplica")], default="pendente", max_length=20)),
                ("justificativa", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("atualizado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("conciliacao", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ocorrencias", to="conciliacao.conciliacao")),
                ("movimentacao", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="ocorrencias", to="conciliacao.movimentacao")),
            ], options={"ordering": ["situacao", "-criado_em"]},
        ),
    ]
