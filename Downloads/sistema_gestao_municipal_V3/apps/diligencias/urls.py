from django.urls import path
from .views import DiligenciaCreate, DiligenciaDetail, DiligenciaList, DiligenciaUpdate, alterar_status, comentar_interno, enviar_diligencia, marcar_notificacao_lida, notificacoes, responder_diligencia

urlpatterns = [
    path("", DiligenciaList.as_view(), name="list_diligencias"),
    path("nova/", DiligenciaCreate.as_view(), name="create_diligencia"),
    path("notificacoes/", notificacoes, name="notificacoes"),
    path("notificacoes/<int:pk>/lida/", marcar_notificacao_lida, name="marcar_notificacao_lida"),
    path("<int:pk>/", DiligenciaDetail.as_view(), name="detail_diligencia"),
    path("<int:pk>/editar/", DiligenciaUpdate.as_view(), name="update_diligencia"),
    path("<int:pk>/enviar/", enviar_diligencia, name="enviar_diligencia"),
    path("<int:pk>/responder/", responder_diligencia, name="responder_diligencia"),
    path("<int:pk>/comentario/", comentar_interno, name="comentar_interno"),
    path("<int:pk>/status/<str:status>/", alterar_status, name="alterar_status_diligencia"),
]
