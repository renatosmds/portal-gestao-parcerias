from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("termos", "0017_alter_termos_extratosbancarios_and_more"),
        ("documentos", "0010_documento_conferencia"),
    ]
    operations = [
        migrations.CreateModel(
            name="PublicacaoParceria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("publicada", models.BooleanField(default=False, verbose_name="Publicada")),
                ("orgao_responsavel", models.CharField(blank=True, max_length=150, verbose_name="Órgão responsável")),
                ("resumo_publico", models.TextField(blank=True, verbose_name="Resumo público")),
                ("publicada_em", models.DateTimeField(blank=True, null=True, verbose_name="Publicada em")),
                ("motivo_restricao", models.TextField(blank=True, verbose_name="Motivo da restrição")),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("publicada_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="parcerias_publicadas", to=settings.AUTH_USER_MODEL, verbose_name="Publicada por")),
                ("termo", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="publicacao_transparencia", to="termos.termos", verbose_name="Termo")),
            ],
            options={"verbose_name": "Publicação de parceria", "verbose_name_plural": "Publicações de parcerias", "ordering": ["-publicada", "termo__numtermo", "termo__termo"]},
        ),
        migrations.CreateModel(
            name="PublicacaoDocumento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("classificacao", models.CharField(choices=[("publico", "Público"), ("interno", "Interno"), ("restrito", "Restrito"), ("dado_pessoal", "Dado pessoal"), ("dado_sensivel", "Dado pessoal sensível")], default="interno", max_length=24, verbose_name="Classificação")),
                ("publicado", models.BooleanField(default=False, verbose_name="Publicado")),
                ("titulo_publico", models.CharField(blank=True, max_length=180, verbose_name="Título público")),
                ("descricao_publica", models.TextField(blank=True, verbose_name="Descrição pública")),
                ("motivo_restricao", models.TextField(blank=True, verbose_name="Motivo da restrição")),
                ("publicado_em", models.DateTimeField(blank=True, null=True, verbose_name="Publicado em")),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("documento", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="publicacao_transparencia", to="documentos.documento", verbose_name="Documento")),
                ("publicado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="documentos_publicados", to=settings.AUTH_USER_MODEL, verbose_name="Publicado por")),
            ],
            options={"verbose_name": "Publicação de documento", "verbose_name_plural": "Publicações de documentos", "ordering": ["-publicado", "documento__descricao"]},
        ),
        migrations.CreateModel(
            name="HistoricoPublicacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("acao", models.CharField(choices=[("publicar", "Publicar"), ("retirar", "Retirar da transparência"), ("reclassificar", "Reclassificar"), ("alterar", "Alterar dados públicos")], max_length=24)),
                ("detalhes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("documento", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="historicos_publicacao", to="documentos.documento")),
                ("termo", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="historicos_publicacao", to="termos.termos")),
                ("usuario", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Histórico de publicação", "verbose_name_plural": "Históricos de publicação", "ordering": ["-criado_em"]},
        ),
    ]
