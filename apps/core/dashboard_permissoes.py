from apps.core.models import (
    ConfiguracaoDashboardGrupo,
    ConfiguracaoDashboardUsuario,
)
from apps.core.permissoes_modulos import modulos_liberados


def modulos_dashboard_usuario(user):
    """
    Retorna o conjunto de m?dulos que podem ser exibidos
    no Dashboard do usu?rio.

    A configura??o do Dashboard nunca concede acesso.
    Ela apenas filtra m?dulos j? autorizados pela
    matriz de permiss?es do PGP.
    """

    modulos_acesso = set(modulos_liberados(user))

    if not modulos_acesso:
        return set()

    configuracoes_usuario = {
        config.modulo: config.estado
        for config in ConfiguracaoDashboardUsuario.objects.filter(
            usuario=user,
            modulo__in=modulos_acesso,
        )
    }

    grupos_ids = list(
        user.groups.values_list(
            "id",
            flat=True,
        )
    )

    configuracoes_grupos = {}

    if grupos_ids:
        for config in (
            ConfiguracaoDashboardGrupo.objects
            .filter(
                grupo_id__in=grupos_ids,
                modulo__in=modulos_acesso,
            )
            .values(
                "modulo",
                "exibir",
            )
        ):
            configuracoes_grupos.setdefault(
                config["modulo"],
                [],
            ).append(
                config["exibir"]
            )

    resultado = set()

    for modulo in modulos_acesso:

        estado_usuario = configuracoes_usuario.get(
            modulo
        )

        if (
            estado_usuario
            == ConfiguracaoDashboardUsuario.Estado.MOSTRAR
        ):
            resultado.add(modulo)
            continue

        if (
            estado_usuario
            == ConfiguracaoDashboardUsuario.Estado.OCULTAR
        ):
            continue

        valores_grupo = configuracoes_grupos.get(
            modulo,
            [],
        )

        if valores_grupo:

            if any(valores_grupo):
                resultado.add(modulo)

            continue

        # Fallback compat?vel:
        # sem configura??o espec?fica, preserva o
        # comportamento atual do Dashboard.
        resultado.add(modulo)

    return resultado
