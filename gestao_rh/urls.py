from apps.analise.api.viewsets import AnaliseViewSet
from apps.clientes.api.viewsets import ClientesViewSet
from apps.conferencia3.api.viewsets import Conferencia3ViewSet
from apps.core import views
# from apps.curso.api.views import CursoViewSet
from apps.funcionarios.api.views import FuncionarioViewSet
from apps.parcerias.api.viewsets import ParceriasViewSet
from apps.prestacao.api.viewsets import PrestacaoViewSet
from apps.receitas.api.viewsets import ReceitasViewSet
from apps.registro_hora_extra.api.views import RegistroHoraExtraViewSet
from apps.termos.api.views import TermosViewSet
from django.conf import settings
#from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from rest_framework import routers

from .views import articles
from .views import fname
from .views import hello

# from home import urls as home_urls
# from django.contrib.auth import views as auth_views


# from clientes1 import urls as clientes1_urls
# from colaboradores import urls as colaboradores_urls
# from colaboradores2 import urls as colaboradores2_urls
# from cadastro import urls as cadastro_urls

# from dispensa import urls as dispensa_urls
# from documento import urls as documento_urls
# from person1 import urls as person1_urls
# from plano import urls as plano_urls
# from plano1 import urls as plano1_urls
# from termo import urls as termo_urls
# from prestacao import urls as prestacao_urls
# from produtos import urls as produtos_urls
# from conferencia import urls as conferencia_urls
# from conferencia2 import urls as conferencia2_urls
# from parcerias import urls as conferencia3_urls
# from prestacaoContas import urls as prestacaoContas_urls
# from produto import urls as produto_urls

# from gestor import urls as gestor_urls
# from cma import urls as cma_urls

# from folha import urls as folha_urls
# from venda_produtos import urls as venda_produtos_urls
# from vendas import urls as vendas_urls
# from vendas1 import urls as vendas1_urls

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(
    r'api/funcionarios',
    FuncionarioViewSet,
    basename='funcionario')
router.register(r'api/banco-horas', RegistroHoraExtraViewSet)
router.register(r'prestacao', PrestacaoViewSet)
router.register(r'termos', TermosViewSet)
router.register(r'clientes', ClientesViewSet)
router.register(r'receitas', ReceitasViewSet)
router.register(
    r'analise',
    AnaliseViewSet,
    basename='analise',
)
router.register(r'parcerias', ParceriasViewSet)
router.register(r'conferencia3', Conferencia3ViewSet)
#router.register(r'bpm', Conferencia3ViewSet)

urlpatterns = [
                  path('', include('apps.core.urls')), # ok
                  path('', include('home.urls')),  # no original 'apps.core.urls' # ok
                  path('funcionarios/', include('apps.funcionarios.urls')),
                  path('empresa/', include('apps.empresas.urls')),
                  path('admin/', admin.site.urls),
                  path('accounts/', include('django.contrib.auth.urls')),
                  path('login/', RedirectView.as_view(pattern_name='login', permanent=False), name='legacy_login'),


                  path('hello/', hello),
                  path('articles/<int:year>/', articles),
                  path('pessoa/<str:nome>/', fname),
                  # path('pessoa/<str:nome>/', fname2),
                  path('curso/', include('apps.curso.urls')),
                  path('clientes/', include('apps.clientes.urls')),
                  path('departamentos/', include('apps.departamentos.urls')),
                  path('documentos/', include('apps.documentos.urls')),
                  path('diligencias/', include('apps.diligencias.urls')),
                  path('horas-extras/', include('apps.registro_hora_extra.urls')),
                  path('fornecedor/', include('apps.fornecedores.urls')),
                  # path('jet/', include('jet.urls')),  # jet URLS
                  # path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # jet/dashboard URLS
                  # path('suit/', include('suit.urls')),  # suit URLS
                  path('grappelli/', include('grappelli.urls')),  # grappelli URLS
                  # path('admin/', admin.site.urls),  # admin site

                  path('conferencia3/', include('apps.conferencia3.urls')),
                  #path('bpm/', include('apps.bpm.urls')),
                  path('termos/', include('apps.termos.urls')),
                  path('prestacao/', include('apps.prestacao.urls')),
                  path('receitas/', include('apps.receitas.urls')),
                  path('relatorios/', include('apps.relatorios.urls')),
                  path('analise/', include('apps.analise.urls')),
                  path('assistente-ia/', include('apps.assistente_ia.urls')),
                  path('transparencia/', include('apps.transparencia.urls')),
                  path('conciliacao/', include('apps.conciliacao.urls')),
                  path('metas/', include('apps.metas.urls')),
                  path('ajuda-contextual/', include('apps.ajuda_contextual.urls')),
                  path('treinamento/', include('apps.treinamento.urls')),
                  path('suporte/', include('apps.suporte.urls')),
                  path('lancamentos/', include('apps.lancamentos.urls')),
                  path('importacoes/', include('apps.importacoes.urls')),
                  path('parcerias/', include('apps.parcerias.urls')),
                  #url(r'^', include(router.urls)),
                  #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
                  # path('clientes1/', include(clientes1_urls)),
                  # path('colaboradores/', include(colaboradores_urls)),
                  # path('colaboradores2/', include(colaboradores2_urls)),
                  # path('cadastro/', include(cadastro_urls)),
                  # path('dispensa/', include(dispensa_urls)),
                  # path('documento/', include(documento_urls)),
                  # path('person1/', include(person1_urls)),
                  # path('plano/', include(plano_urls)),
                  # path('plano1/', include(plano1_urls)),
                  # path('termo/', include(termo_urls)),
                  # path('prestacao/', include(prestacao_urls)),
                  # path('prestacaoContas/', include(prestacaoContas_urls)),
                  # path('produto/', include(produto_urls)),
                  # path('produtos/', include(produtos_urls)),
                  # path('conferencia/', include(conferencia_urls)),
                  # path('conferencia2/', include(conferencia2_urls)),
                  # path('parcerias/', include(conferencia3_urls)),
                  # path('gestor/', include(gestor_urls)),
                  # path('cma/', include(cma_urls)),
                  # path('folha/', include(folha_urls)),
                  # path('venda_produtos/', include(venda_produtos_urls)),
                  # path('vendas/', include(vendas_urls)),
                  # path('vendas1/', include(vendas1_urls)),
                  # path('login/', auth_views.LoginView.as_view(), name='login'),
                  # path('logout/', auth_views.LogoutView.as_view(), name='logout'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if getattr(settings, 'DEBUG_TOOLBAR_AVAILABLE', False):
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

admin.site.site_header = "Portal de Gestão de Parcerias"
admin.site.index_title = "Administração do Portal"
admin.site.site_title = "Portal de Gestão de Parcerias"

handler400 = 'gestao_rh.error_views.bad_request'
handler403 = 'gestao_rh.error_views.permission_denied'
handler404 = 'gestao_rh.error_views.page_not_found'
handler500 = 'gestao_rh.error_views.server_error'
