def access_context(request):
    """
    Informações leves de acesso para o cabeçalho.

    Nunca presume que todo usuário possui Funcionario/Empresa vinculados.
    """
    user = getattr(request, "user", None)

    context = {
        "perfil_usuario": "",
        "empresa_usuario": "",
    }

    if not user or not user.is_authenticated:
        return context

    if user.is_superuser:
        context["perfil_usuario"] = "Administrador"
    else:
        group = user.groups.order_by("name").first()
        context["perfil_usuario"] = group.name if group else "Sem perfil"

    try:
        funcionario = user.funcionario
        empresa = getattr(funcionario, "empresa", None)
        if empresa:
            context["empresa_usuario"] = str(empresa)
    except Exception:
        # Usuários técnicos, administradores e contas ainda não vinculadas
        # continuam podendo acessar as telas autorizadas.
        pass

    return context
