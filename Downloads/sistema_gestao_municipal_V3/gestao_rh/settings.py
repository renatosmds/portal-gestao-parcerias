
import os
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

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [
    'sistema-gestao-municipal.herokuapp.com',
    'localhost',
    '127.0.0.1',
    # '34.238.131.159',
    # '34.202.149.53',
    # 'sistema-gestao-municipal.rlfsolutions.com.br',
    # 'rlfsolutions.com.br',
    # 'www.rlfsolutions.com.br',
]

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
    'debug_toolbar',
    # 'import-export',
]

INTERNAL_IPS = ['127.0.0.1']

#   ADMINS = [('Gregory', 'django@gregorypacheco.com.br')]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
    'debug_toolbar.middleware.DebugToolbarMiddleware',

]

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

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
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

DATABASES = {
      'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
       },
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'dc7td6n6idjhrb',
    #     'USER': 'xblzifmmnchdfj',
    #     'PASSWORD': '66dbfa4d7ebe483ea60eca648648ba19998bcc29004b3e28c48e079baedacc26',
    #     'HOST': 'ec2-107-22-7-9.compute-1.amazonaws.com',
    #     'PORT': '5432',
    # },
    #    'mysql': {
    #        'ENGINE': 'django.db.backends.mysql',
    #        'NAME': 'gestao_rh',
    #        'USER': 'user_RLF',
    #        'PASSWORD': 'r70742524H%!',
    #        'HOST': 'localhost',
    #        'PORT': '5432',
    #    },
}

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
