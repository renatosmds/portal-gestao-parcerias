from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="PreferenciaTour",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tour_concluido", models.BooleanField(default=False)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("usuario", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="preferencia_tour", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Preferência de tour", "verbose_name_plural": "Preferências de tour"},
        ),
        migrations.CreateModel(
            name="ProgressoTreinamento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("modulo", models.CharField(max_length=80)),
                ("concluido", models.BooleanField(default=False)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progressos_treinamento", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Progresso de treinamento", "verbose_name_plural": "Progressos de treinamento", "ordering": ["modulo"], "unique_together": {("usuario", "modulo")}},
        ),
    ]
