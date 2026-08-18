import sys
import os
from importlib.util import find_spec
# import pandas as pd
# import django
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_rh.settings')
# django.setup()
#
# from gestao_rh.models import Termos
#
# def importar_excel():
#
#     df - pd.read_excel ('caminho/para/seu/arquivo.xlsx')
#
#     for index, row in df.iterrows():
#         Termos.objects.create(
#             nome-row['nome_coluna_excel'],
#             documento-row['documento_coluna_excel'],
#             idade-row['idade_coluna_excel'],
#         )
#     print("Importação concluída!")
#
# if __name__== '__main__':
#     importar_excel()

# from django.utils.translation import ugettext_lazy as _
from decouple import config
from dj_database_url import parse as dburl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config('SECRET_KEY', default='dev-inseguro-troque-no-env')
DEBUG = config('DEBUG', default=False, cast=bool)

def _csv_config(name, default=''):
    return [item.strip() for item in config(name, default=default).split(',') if item.strip()]

ALLOWED_HOSTS = _csv_config('ALLOWED_HOSTS', '127.0.0.1,localhost')
CSRF_TRUSTED_ORIGINS = _csv_config('CSRF_TRUSTED_ORIGINS', '')
PGP_SESSION_IDLE_MINUTES = config('PGP_SESSION_IDLE_MINUTES', default=60, cast=int)
PGP_MAX_UPLOAD_MB = config('PGP_MAX_UPLOAD_MB', default=20, cast=int)
PGP_AMBIENTE_DEMO = config('PGP_AMBIENTE_DEMO', default=False, cast=bool)
PGP_DEMO_MENSAGEM = config(
    'PGP_DEMO_MENSAGEM',
    default='Ambiente exclusivamente demonstrativo. Todos os dados apresentados são fictícios.',
)

# Sprint 23 — análise assistida. A integração externa permanece desativada por padrão.
PGP_IA_ATIVA = config('PGP_IA_ATIVA', default=False, cast=bool)
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
PGP_IA_MODELO = config('PGP_IA_MODELO', default='')
PGP_IA_LIMITE_PAGINAS = config('PGP_IA_LIMITE_PAGINAS', default=10, cast=int)
PGP_IA_LIMITE_TAMANHO_MB = config('PGP_IA_LIMITE_TAMANHO_MB', default=15, cast=int)
PGP_IA_ANONIMIZAR = config('PGP_IA_ANONIMIZAR', default=True, cast=bool)
DATA_UPLOAD_MAX_MEMORY_SIZE = PGP_MAX_UPLOAD_MB * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = min(PGP_MAX_UPLOAD_MB, 5) * 1024 * 1024
PORTABLE_DATA_DIR = config('PGP_DATA_DIR', default='').strip()

INSTALLED_APPS = [
    'grappelli',
    # 'suit',
    # 'jet.dashboard',
    # 'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'bootstrapform',
    'rest_framework',
    'rest_framework.authtoken',

    'apps.analise',
    'apps.assistente_ia.apps.AssistenteIaConfig',
    'apps.regras.apps.RegrasConfig',
    'apps.planos_trabalho.apps.PlanosTrabalhoConfig',
    'apps.transparencia.apps.TransparenciaConfig',
    'apps.conciliacao.apps.ConciliacaoConfig',
    'apps.metas.apps.MetasConfig',
    'apps.ajuda_contextual.apps.AjudaContextualConfig',
    'apps.treinamento.apps.TreinamentoConfig',
    'apps.suporte.apps.SuporteConfig',
    #'apps.app_antiga',
    'apps.clientes',
    'apps.conferencia3',
    #'apps.bpm',
    'apps.core',
    'apps.departamentos',  # gestão_rh
    'apps.documentos',  # gestão_rh
    # 'apps.diligencias',
    'apps.diligencias.apps.DiligenciasConfig',
    'apps.empresas',  # gestão_rh
    'apps.fornecedores',
    'apps.funcionarios',  # gestão_rh
    'apps.lancamentos',
    'apps.importacoes.apps.ImportacoesConfig',
    'apps.parcerias',
    'apps.prestacao',
    'apps.receitas',
    'apps.relatorios.apps.RelatoriosConfig',
    'apps.registro_hora_extra',  # gestão_rh
    'apps.termos',
    'apps.curso',
    #'menu',
    'home',

    'django_celery_results',
    'django_celery_beat',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.google',

    'django.contrib.humanize',


    # 'gestao_clientes',
    # 'cadastro',
    # 'clientes1',
    # 'cma',
    # 'colaboradores',
    # 'colaboradores2',
    # 'conferencia',
    # 'conferencia2',
    # 'dispensa',
    # 'documento',
    # 'folha',
    # 'gestor',
    # 'person1',
    # 'plano',
    # 'plano1',
    # 'prestacaoContas',
    # 'produto',
    # 'produtos',
    # 'receitas1',
    # 'receitas2',
    # 'termo',
    # 'venda_produtos',
    # 'vendas',
    # 'vendas1',
    # 'import-export',
]

DEBUG_TOOLBAR_AVAILABLE = bool(DEBUG and find_spec('debug_toolbar'))
if DEBUG_TOOLBAR_AVAILABLE:
    INSTALLED_APPS.append('debug_toolbar')

INTERNAL_IPS = ['127.0.0.1']
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'gestao_rh.debug.show_toolbar',
}


#   ADMINS = [('Gregory', 'django@gregorypacheco.com.br')]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Serve os arquivos coletados também com DEBUG=False e no modo portátil.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'allauth.account.middleware.AccountMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'custom_middleware.AppMetaData',
    # 'whitenoise.middleware.WhiteNoiseMiddleware',

]

MIDDLEWARE.insert(6, 'gestao_rh.middleware.SessionIdleTimeoutMiddleware')
MIDDLEWARE.append('gestao_rh.middleware.AuditRequestMiddleware')
if DEBUG_TOOLBAR_AVAILABLE:
    # Após AuthenticationMiddleware para que o callback possa verificar o usuário.
    MIDDLEWARE.insert(7, 'debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'gestao_rh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # 'django.core.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.access_context',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

#WSGI_APPLICATION = 'gestao_rh.wsgi.application'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# default_dburl = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')

# DATABASES = {
#    'default': config('DATABASE_URL', default=default_dburl, cast=dburl),
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True  # Multi idiomas

USE_L10N = True  # padrão True ( Multi localização)

USE_TZ = True  # Time zone

STATIC_URL = '/static/'

# Arquivos-fonte usados durante o desenvolvimento.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Destino do collectstatic. Mantido separado dos arquivos-fonte.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise mantém CSS/JS disponíveis em homologação, produção local e pendrive.
# O backend simples evita falhas por manifesto durante o desenvolvimento incremental.
IS_TESTING = "test" in sys.argv

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if IS_TESTING
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}
WHITENOISE_MAX_AGE = 31536000 if not DEBUG else 0

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(PORTABLE_DATA_DIR or BASE_DIR, 'media')
# MEDIA_ROOT = 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'

LOGOUT_REDIRECT_URL = 'login'

CELERY_RESULT_BACKEND = 'django-db'

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

# DEFAULT_DB_ALIAS = 'default'

DATABASE_ROUTERS = ['gestao_rh.DBRoutes.DBRoutes']

# PostgreSQL em produção (Render) e SQLite no desenvolvimento local/portátil.
default_dburl = 'sqlite:///' + os.path.join(PORTABLE_DATA_DIR or BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': config(
        'DATABASE_URL',
        default=default_dburl,
        cast=dburl,
    )
}

# O Render encerra a conexão ociosa; conexões persistentes melhoram o desempenho.
if config('DATABASE_URL', default='').startswith(('postgres://', 'postgresql://')):
    DATABASES['default']['CONN_MAX_AGE'] = 60
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

# LANGUAGES = (
#     ('en', _('English')),
#     ('pt', _('Portugues')),
#     ('es', _('Spanish')),
# )

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# from .local_settings import *

# AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = 'sistema-gestao-municipal1'
# AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400',
# }
# AWS_LOCATION = 'static'
#
# STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# EMAIL_HOST = config('EMAIL_HOST')
# EMAIL_PORT = 25
# EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# EMAIL_USE_TLS = False

THOUSAND_SEPARATOR = '.',
USE_THOUSAND_SEPARATOR = True

# DATE_INPUT_FORMAT = ["%d/%m/%Y"]

DATE_FORMAT = 'd/m/y'


# Mantém compatibilidade com os models e migrations legados do projeto.
# Evita a criação automática de BigAutoField e elimina os avisos W042.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# Render e outros proxies HTTPS informam o protocolo por X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Segurança por ambiente. Em produção, configure DEBUG=False no .env.
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool) if not DEBUG else False

LOG_DIR = os.path.join(PORTABLE_DATA_DIR or BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'pgp': {'format': '{asctime} {levelname} {message}', 'style': '{'},
    },
    'handlers': {
        'audit_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'auditoria.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'pgp',
            'encoding': 'utf-8',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'erros.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'pgp',
            'encoding': 'utf-8',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'pgp.audit': {'handlers': ['audit_file'], 'level': 'INFO', 'propagate': False},
        'django.request': {'handlers': ['error_file'], 'level': 'ERROR', 'propagate': True},
    },
}
