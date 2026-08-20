from apps.pareceres.models import ItemParecer, ParecerTecnico


def usuario_acesso_global(user):
    return bool(
        user
        and user.is_authenticated
        and user.is_superuser
    )


def empresa_do_usuario(user):
    if not user or not user.is_authenticated:
        return None

    try:
        funcionario = user.funcionario
    except Exception:
        return None

    if not getattr(funcionario, "ativo", False):
        return None

    return getattr(funcionario, "empresa", None)


def pareceres_permitidos(user):
    qs = ParecerTecnico.objects.select_related(
        "empresa",
        "prestacao",
        "elaborado_por",
        "revisado_por",
    )

    if usuario_acesso_global(user):
        return qs

    empresa = empresa_do_usuario(user)

    if not empresa:
        return qs.none()

    return qs.filter(
        empresa=empresa
    )


def itens_parecer_permitidos(user):
    return ItemParecer.objects.select_related(
        "parecer",
        "parecer__empresa",
        "parecer__prestacao",
        "diligencia",
        "documento",
        "lancamento",
    ).filter(
        parecer__in=pareceres_permitidos(user)
    )
