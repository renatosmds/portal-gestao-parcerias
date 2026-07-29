from .dashboard import usuario_eh_osc


def access_context(request):
    """Informações leves de acesso usadas pelo cabeçalho e pelo menu."""
    user = getattr(request, "user", None)

    context = {
        "perfil_usuario": "",
        "empresa_usuario": "",
        "usuario_area_osc": False,
        "area_portal": "Portal de Gestão de Parcerias",
    }

    if not user or not user.is_authenticated:
        return context

    context["usuario_area_osc"] = usuario_eh_osc(user)
    context["area_portal"] = (
        "Área da OSC" if context["usuario_area_osc"] else "Área do Órgão Público"
    )

    if user.is_superuser:
        context["perfil_usuario"] = "Administrador da Plataforma"
    else:
        group = user.groups.order_by("name").first()
        context["perfil_usuario"] = group.name if group else "Sem perfil definido"

    try:
        funcionario = user.funcionario
        empresa = getattr(funcionario, "empresa", None)
        if empresa:
            context["empresa_usuario"] = str(empresa)
    except Exception:
        # Contas técnicas e administradores podem não possuir vínculo funcional.
        pass

    return context
