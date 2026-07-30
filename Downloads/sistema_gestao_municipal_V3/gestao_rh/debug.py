"""Regras de exibição da Django Debug Toolbar."""


def show_toolbar(request):
    """Exibe a toolbar somente ao superusuário autenticado em ambiente DEBUG."""
    user = getattr(request, "user", None)
    return bool(user and user.is_authenticated and user.is_superuser)
