from apps.core.dashboard_widgets import WIDGETS_DASHBOARD
from apps.core.models import (
    ConfiguracaoDashboardWidgetGrupo,
    ConfiguracaoDashboardWidgetUsuario,
)


def widgets_dashboard_usuario(user):
    """
    Retorna os blocos visuais habilitados no Dashboard.

    Precedencia:
    1. configuracao individual;
    2. configuracao dos grupos;
    3. ausencia de configuracao = exibir.
    """

    if not getattr(user, "is_authenticated", False):
        return set()

    configuracoes_usuario = {
        item.widget: item.estado
        for item in ConfiguracaoDashboardWidgetUsuario.objects.filter(
            usuario=user
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
        for item in (
            ConfiguracaoDashboardWidgetGrupo.objects
            .filter(
                grupo_id__in=grupos_ids,
            )
            .values(
                "widget",
                "exibir",
            )
        ):
            configuracoes_grupos.setdefault(
                item["widget"],
                [],
            ).append(
                item["exibir"]
            )

    resultado = set()

    for widget in WIDGETS_DASHBOARD:

        estado = configuracoes_usuario.get(
            widget
        )

        if (
            estado
            == ConfiguracaoDashboardWidgetUsuario.Estado.MOSTRAR
        ):
            resultado.add(widget)
            continue

        if (
            estado
            == ConfiguracaoDashboardWidgetUsuario.Estado.OCULTAR
        ):
            continue

        valores_grupo = configuracoes_grupos.get(
            widget,
            [],
        )

        if valores_grupo:
            if any(valores_grupo):
                resultado.add(widget)

            continue

        # Compatibilidade com o Dashboard atual:
        # sem configuracao, o bloco continua visivel.
        resultado.add(widget)

    return resultado
