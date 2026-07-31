from django.contrib import admin
from .models import ComentarioInterno, Diligencia, Notificacao, RespostaDiligencia

admin.site.register(Diligencia)
admin.site.register(RespostaDiligencia)
admin.site.register(ComentarioInterno)
admin.site.register(Notificacao)
