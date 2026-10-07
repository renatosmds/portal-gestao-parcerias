from django.db import migrations


def migrar_cadastros(apps, schema_editor):
    Funcionario = apps.get_model(
        "funcionarios",
        "Funcionario",
    )
    Cargo = apps.get_model(
        "funcionarios",
        "Cargo",
    )
    Nivel = apps.get_model(
        "funcionarios",
        "Nivel",
    )
    Equipamento = apps.get_model(
        "funcionarios",
        "Equipamento",
    )

    for funcionario in Funcionario.objects.all().iterator():
        empresa_id = funcionario.empresa_id

        if not empresa_id:
            continue

        cargo = (funcionario.cargo or "").strip()

        if cargo and cargo != "--":
            obj, _ = Cargo.objects.get_or_create(
                empresa_id=empresa_id,
                nome=cargo,
                defaults={
                    "ativo": True,
                    "descricao": "",
                },
            )

            funcionario.cargo_cadastro_id = obj.pk

        nivel = (funcionario.nivel or "").strip()

        if nivel and nivel != "--":
            obj, _ = Nivel.objects.get_or_create(
                empresa_id=empresa_id,
                nome=nivel,
                defaults={
                    "ativo": True,
                    "descricao": "",
                    "ordem": 0,
                },
            )

            funcionario.nivel_cadastro_id = obj.pk

        equipamento = (
            funcionario.equipamento or ""
        ).strip()

        if equipamento and equipamento != "--":
            obj, _ = Equipamento.objects.get_or_create(
                empresa_id=empresa_id,
                nome=equipamento,
                defaults={
                    "ativo": True,
                    "descricao": "",
                },
            )

            funcionario.equipamento_cadastro_id = obj.pk

        funcionario.save(
            update_fields=[
                "cargo_cadastro",
                "nivel_cadastro",
                "equipamento_cadastro",
            ]
        )


def desfazer_migracao(apps, schema_editor):
    Funcionario = apps.get_model(
        "funcionarios",
        "Funcionario",
    )

    Funcionario.objects.update(
        cargo_cadastro=None,
        nivel_cadastro=None,
        equipamento_cadastro=None,
    )


class Migration(migrations.Migration):

    dependencies = [
        (
            "funcionarios",
            "0033_cargo_funcionario_cargo_cadastro_equipamento_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            migrar_cadastros,
            desfazer_migracao,
        ),
    ]
