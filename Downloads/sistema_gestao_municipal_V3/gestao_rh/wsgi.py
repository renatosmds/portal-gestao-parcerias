"""WSGI config do Portal de Gestão de Parcerias."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestao_rh.settings")
application = get_wsgi_application()
