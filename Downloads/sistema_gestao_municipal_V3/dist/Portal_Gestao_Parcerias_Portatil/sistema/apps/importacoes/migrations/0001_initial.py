from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Importacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("osc", "OSCs / Empresas"), ("termo", "Termos"), ("prestacao", "Prestações de contas"), ("lancamento", "Lançamentos")], max_length=20)),
                ("arquivo_nome", models.CharField(max_length=255)),
                ("sistema_origem", models.CharField(blank=True, default="Arquivo externo", max_length=80)),
                ("situacao", models.CharField(choices=[("validacao", "Em validação"), ("confirmada", "Confirmada"), ("parcial", "Parcialmente aplicada"), ("cancelada", "Cancelada"), ("erro", "Com erro")], default="validacao", max_length=20)),
                ("cabecalhos", models.JSONField(blank=True, default=list)),
                ("linhas", models.JSONField(blank=True, default=list)),
                ("erros", models.JSONField(blank=True, default=list)),
                ("total_lido", models.PositiveIntegerField(default=0)),
                ("total_novos", models.PositiveIntegerField(default=0)),
                ("total_atualizados", models.PositiveIntegerField(default=0)),
                ("total_duplicados", models.PositiveIntegerField(default=0)),
                ("total_erros", models.PositiveIntegerField(default=0)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("confirmado_em", models.DateTimeField(blank=True, null=True)),
                ("criado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Importação", "verbose_name_plural": "Importações", "ordering": ["-criado_em"]},
        )
    ]
