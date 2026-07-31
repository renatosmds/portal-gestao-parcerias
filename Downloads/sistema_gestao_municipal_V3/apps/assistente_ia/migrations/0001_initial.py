from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("documentos", "0010_documento_conferencia"),
        ("empresas", "0015_alter_empresa_options_alter_empresa_conferencia3_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProcessamentoAssistido",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("concluido", "Concluído"), ("revisado", "Revisado"), ("erro", "Com erro")], default="concluido", max_length=20)),
                ("decisao_revisor", models.CharField(choices=[("pendente", "Aguardando revisão"), ("aceito", "Sugestão aceita"), ("alterado", "Sugestão alterada"), ("rejeitado", "Sugestão rejeitada")], default="pendente", max_length=20, verbose_name="Decisão do revisor")),
                ("resumo", models.TextField(blank=True)),
                ("rascunho_inconformidade", models.TextField(blank=True)),
                ("rascunho_diligencia", models.TextField(blank=True)),
                ("rascunho_recomendacao", models.TextField(blank=True)),
                ("observacoes_revisor", models.TextField(blank=True)),
                ("ia_externa_utilizada", models.BooleanField(default=False)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("revisado_em", models.DateTimeField(blank=True, null=True)),
                ("documento", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="processamentos_assistidos", to="documentos.documento", verbose_name="Documento")),
                ("empresa", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="processamentos_assistidos", to="empresas.empresa", verbose_name="OSC / Empresa")),
                ("revisado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="processamentos_assistidos_revisados", to=settings.AUTH_USER_MODEL, verbose_name="Revisado por")),
                ("solicitado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="processamentos_assistidos_solicitados", to=settings.AUTH_USER_MODEL, verbose_name="Solicitado por")),
            ],
            options={"verbose_name": "Processamento assistido", "verbose_name_plural": "Processamentos assistidos", "ordering": ["-criado_em", "-id"]},
        ),
        migrations.CreateModel(
            name="AchadoAssistido",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=60)),
                ("severidade", models.CharField(choices=[("info", "Informativo"), ("alerta", "Alerta"), ("critico", "Crítico")], default="alerta", max_length=10)),
                ("titulo", models.CharField(max_length=180)),
                ("descricao", models.TextField()),
                ("ordem", models.PositiveIntegerField(default=0)),
                ("processamento", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="achados", to="assistente_ia.processamentoassistido")),
            ],
            options={"verbose_name": "Achado assistido", "verbose_name_plural": "Achados assistidos", "ordering": ["ordem", "id"]},
        ),
    ]
