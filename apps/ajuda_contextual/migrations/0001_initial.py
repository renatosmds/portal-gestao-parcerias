from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="AjudaContextual", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("modulo", models.CharField(db_index=True, max_length=100)), ("formulario", models.CharField(blank=True, max_length=150)),
            ("campo", models.CharField(db_index=True, max_length=150)), ("chave", models.SlugField(max_length=250, unique=True)),
            ("titulo", models.CharField(max_length=200)), ("ajuda_curta", models.CharField(blank=True, max_length=300)),
            ("what", models.TextField(blank=True, verbose_name="O que é")), ("why", models.TextField(blank=True, verbose_name="Por que")),
            ("who", models.TextField(blank=True, verbose_name="Quem")), ("when", models.TextField(blank=True, verbose_name="Quando")),
            ("where", models.TextField(blank=True, verbose_name="Onde")), ("how", models.TextField(blank=True, verbose_name="Como")),
            ("how_much", models.TextField(blank=True, verbose_name="Quanto / impacto")), ("exemplo", models.TextField(blank=True)),
            ("atencao", models.TextField(blank=True)), ("referencia", models.CharField(blank=True, max_length=300)),
            ("publica", models.BooleanField(default=False, help_text="Permite consulta sem autenticação em páginas públicas.")),
            ("ativo", models.BooleanField(default=True)), ("versao", models.PositiveIntegerField(default=1)),
            ("criado_em", models.DateTimeField(auto_now_add=True)), ("atualizado_em", models.DateTimeField(auto_now=True)),
            ("criado_por", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ajudas_contextuais_criadas", to=settings.AUTH_USER_MODEL)),
        ], options={"verbose_name":"Ajuda contextual","verbose_name_plural":"Ajudas contextuais","ordering":["modulo","formulario","campo"]}),
        migrations.AddIndex(model_name="ajudacontextual", index=models.Index(fields=["modulo","campo","ativo"], name="ajuda_conte_modulo_4a4f6b_idx")),
        migrations.CreateModel(name="AcessoAjuda", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("caminho", models.CharField(blank=True, max_length=300)), ("util", models.BooleanField(blank=True, null=True)),
            ("criado_em", models.DateTimeField(auto_now_add=True)),
            ("ajuda", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="acessos", to="ajuda_contextual.ajudacontextual")),
            ("usuario", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
        ], options={"verbose_name":"Acesso à ajuda","verbose_name_plural":"Acessos às ajudas","ordering":["-criado_em"]}),
    ]
