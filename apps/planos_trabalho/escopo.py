from django.core.exceptions import ObjectDoesNotExist

from apps.metas.models import MetaExecucao
from apps.termos.models import Termos

from .models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)


def usuario_acesso_global(user):
    """
    Apenas superusuário possui acesso transversal nesta fase.

    Usuários staff comuns continuam submetidos ao escopo
    da própria Empresa, evitando acesso global implícito.
    """
    return bool(
        user
        and user.is_authenticated
        and user.is_superuser
    )


def empresa_do_usuario(user):
    if (
        not user
        or not user.is_authenticated
    ):
        return None

    try:
        funcionario = user.funcionario
    except ObjectDoesNotExist:
        return None

    if not funcionario.ativo:
        return None

    return funcionario.empresa


def termos_permitidos(user):
    qs = Termos.objects.all()

    if usuario_acesso_global(user):
        return qs

    empresa = empresa_do_usuario(user)

    if empresa is None:
        return qs.none()

    return qs.filter(
        empresa=empresa
    )


def planos_permitidos(user):
    qs = (
        PlanoTrabalho.objects
        .select_related("termo")
    )

    if usuario_acesso_global(user):
        return qs

    empresa = empresa_do_usuario(user)

    if empresa is None:
        return qs.none()

    return qs.filter(
        termo__empresa=empresa
    )


def itens_permitidos(user):
    qs = (
        ItemPlanoTrabalho.objects
        .select_related(
            "plano",
            "plano__termo",
            "meta",
        )
    )

    if usuario_acesso_global(user):
        return qs

    empresa = empresa_do_usuario(user)

    if empresa is None:
        return qs.none()

    return qs.filter(
        plano__termo__empresa=empresa
    )


def metas_permitidas(
    user,
    *,
    plano=None,
):
    qs = (
        MetaExecucao.objects
        .select_related(
            "prestacao",
            "prestacao__empresa",
        )
    )

    if not usuario_acesso_global(user):
        empresa = empresa_do_usuario(user)

        if empresa is None:
            return qs.none()

        qs = qs.filter(
            prestacao__empresa=empresa
        )

    if plano is not None:
        numero_termo = (
            plano.termo.numtermo or ""
        ).strip()

        if numero_termo:
            qs = qs.filter(
                prestacao__numtermo=numero_termo
            )
        else:
            return qs.none()

    return qs
