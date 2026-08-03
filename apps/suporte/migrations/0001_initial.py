# Generated for Sprint 31
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="ArtigoConhecimento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                ("categoria", models.CharField(choices=[("acesso", "Acesso e usuários"), ("termos", "Termos e parcerias"), ("prestacao", "Prestação de contas"), ("documentos", "Documentos e lançamentos"), ("analise", "Análise, diligência e glosa"), ("conciliacao", "Conciliação bancária"), ("transparencia", "Transparência"), ("tecnico", "Questões técnicas")], max_length=30)),
                ("resumo", models.CharField(blank=True, max_length=300)),
                ("conteudo", models.TextField()),
                ("publico", models.BooleanField(default=False)),
                ("ativo", models.BooleanField(default=True)),
                ("ordem", models.PositiveIntegerField(default=0)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["ordem", "titulo"], "verbose_name": "Artigo da base de conhecimento", "verbose_name_plural": "Artigos da base de conhecimento"},
        ),
        migrations.CreateModel(
            name="ChamadoSuporte",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assunto", models.CharField(max_length=200)),
                ("descricao", models.TextField()),
                ("categoria", models.CharField(choices=[("acesso", "Acesso e usuários"), ("termos", "Termos e parcerias"), ("prestacao", "Prestação de contas"), ("documentos", "Documentos e lançamentos"), ("analise", "Análise, diligência e glosa"), ("conciliacao", "Conciliação bancária"), ("transparencia", "Transparência"), ("tecnico", "Questões técnicas")], max_length=30)),
                ("prioridade", models.CharField(choices=[("baixa", "Baixa"), ("normal", "Normal"), ("alta", "Alta"), ("critica", "Crítica")], default="normal", max_length=10)),
                ("situacao", models.CharField(choices=[("aberto", "Aberto"), ("em_analise", "Em análise"), ("aguardando_usuario", "Aguardando usuário"), ("resolvido", "Resolvido"), ("encerrado", "Encerrado")], default="aberto", max_length=25)),
                ("pagina_origem", models.CharField(blank=True, max_length=500)),
                ("anexo", models.FileField(blank=True, null=True, upload_to="suporte/%Y/%m/")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("encerrado_em", models.DateTimeField(blank=True, null=True)),
                ("responsavel", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="chamados_atendidos", to=settings.AUTH_USER_MODEL)),
                ("solicitante", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chamados_suporte", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-atualizado_em"], "verbose_name": "Chamado de suporte", "verbose_name_plural": "Chamados de suporte"},
        ),
        migrations.CreateModel(
            name="InteracaoChamado",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mensagem", models.TextField()),
                ("interno", models.BooleanField(default=False, help_text="Visível somente para a equipe interna.")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("autor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ("chamado", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="interacoes", to="suporte.chamadosuporte")),
            ],
            options={"ordering": ["criado_em"], "verbose_name": "Interação do chamado", "verbose_name_plural": "Interações dos chamados"},
        ),
    ]
