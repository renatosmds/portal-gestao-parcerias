from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("empresas", "0014_alter_empresa_prestacao"),
        ("prestacao", "0010_workflow_sprint16"),
        ("lancamentos", "0002_glosas_sprint16"),
        ("documentos", "0010_documento_conferencia"),
        ("funcionarios", "0024_sprint17_ponto_folha"),
    ]
    operations = [
        migrations.CreateModel(
            name="Diligencia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assunto", models.CharField(max_length=180)),
                ("descricao", models.TextField()),
                ("fundamento", models.TextField(blank=True)),
                ("prioridade", models.CharField(choices=[("baixa", "Baixa"), ("normal", "Normal"), ("alta", "Alta"), ("urgente", "Urgente")], default="normal", max_length=10)),
                ("status", models.CharField(choices=[("rascunho", "Rascunho"), ("enviada", "Enviada à OSC"), ("visualizada", "Visualizada"), ("em_resposta", "Em resposta"), ("respondida", "Respondida"), ("reanalise", "Em reanalise"), ("atendida", "Atendida"), ("nao_atendida", "Não atendida"), ("cancelada", "Cancelada")], default="rascunho", max_length=20)),
                ("prazo_resposta", models.DateField(blank=True, null=True)),
                ("enviada_em", models.DateTimeField(blank=True, null=True)),
                ("visualizada_em", models.DateTimeField(blank=True, null=True)),
                ("encerrada_em", models.DateTimeField(blank=True, null=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("criada_por", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="diligencias_criadas", to=settings.AUTH_USER_MODEL)),
                ("responsavel", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="diligencias_responsavel", to=settings.AUTH_USER_MODEL)),
                ("empresa", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="diligencias", to="empresas.empresa")),
                ("prestacao", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="diligencias", to="prestacao.prestacao")),
                ("lancamento", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="diligencias", to="lancamentos.lancamento")),
                ("documento", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="diligencias", to="documentos.documento")),
                ("funcionario", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="diligencias", to="funcionarios.funcionario")),
            ],
            options={"ordering": ["status", "prazo_resposta", "-criado_em"], "permissions": [("encerrar_diligencia", "Pode concluir diligência")]},
        ),
        migrations.CreateModel(
            name="RespostaDiligencia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("texto", models.TextField(verbose_name="Resposta / esclarecimento")),
                ("anexo", models.FileField(blank=True, null=True, upload_to="diligencias/respostas/%Y/%m/")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("criada_por", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ("diligencia", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="respostas", to="diligencias.diligencia")),
            ], options={"ordering": ["criado_em"]},
        ),
        migrations.CreateModel(
            name="ComentarioInterno",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("texto", models.TextField()),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("criado_por", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ("diligencia", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comentarios_internos", to="diligencias.diligencia")),
            ], options={"ordering": ["criado_em"]},
        ),
        migrations.CreateModel(
            name="Notificacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=180)),
                ("mensagem", models.CharField(blank=True, max_length=255)),
                ("lida", models.BooleanField(default=False)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("diligencia", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="diligencias.diligencia")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notificacoes_pgp", to=settings.AUTH_USER_MODEL)),
            ], options={"ordering": ["-criado_em"]},
        ),
    ]
