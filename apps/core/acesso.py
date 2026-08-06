from django.core.exceptions import PermissionDenied

GRUPOS_VISAO_GLOBAL = {
    'Administrador do Sistema',
    'Gestor Municipal',
    'Analista de Prestação de Contas',
    'Técnico de Execução',
    'Financeiro',
    'Consulta e Auditoria',
}
GRUPO_OSC = 'Usuário da OSC'


def nomes_grupos(user):
    if not getattr(user, 'is_authenticated', False):
        return set()
    return set(user.groups.values_list('name', flat=True))


def usuario_eh_osc(user):
    return GRUPO_OSC in nomes_grupos(user)


def usuario_pode_ver_todas_empresas(user):
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    return bool(nomes_grupos(user) & GRUPOS_VISAO_GLOBAL)


def empresa_do_usuario(user):
    if not getattr(user, 'is_authenticated', False):
        return None
    try:
        return user.funcionario.empresa
    except Exception:
        return None


def filtrar_por_empresa(queryset, user, campo='empresa'):
    if usuario_pode_ver_todas_empresas(user):
        return queryset
    empresa = empresa_do_usuario(user)
    if not empresa:
        return queryset.none()
    return queryset.filter(**{campo: empresa})


def exigir_empresa_usuario(user):
    empresa = empresa_do_usuario(user)
    if not empresa:
        raise PermissionDenied('Usuário sem OSC/empresa vinculada.')
    return empresa
