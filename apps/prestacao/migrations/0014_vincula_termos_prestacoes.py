from django.db import migrations


def vincular_termos(apps, schema_editor):
    Prestacao = apps.get_model("prestacao", "Prestacao")
    Termos = apps.get_model("termos", "Termos")

    prestacoes = Prestacao.objects.filter(
        termo__isnull=True
    ).exclude(
        numtermo__isnull=True
    )

    for prestacao in prestacoes:
        numero = (prestacao.numtermo or "").strip()

        if not numero or not prestacao.empresa_id:
            continue

        candidatos = Termos.objects.filter(
            empresa_id=prestacao.empresa_id,
            numtermo__iexact=numero,
        )

        if candidatos.count() == 1:
            Prestacao.objects.filter(
                pk=prestacao.pk
            ).update(
                termo_id=candidatos.values_list(
                    "pk",
                    flat=True,
                ).first()
            )


def desvincular_termos(apps, schema_editor):
    Prestacao = apps.get_model("prestacao", "Prestacao")

    Prestacao.objects.update(termo=None)


class Migration(migrations.Migration):
    dependencies = [
        ("prestacao", "0013_prestacao_termo"),
    ]

    operations = [
        migrations.RunPython(
            vincular_termos,
            desvincular_termos,
        ),
    ]
