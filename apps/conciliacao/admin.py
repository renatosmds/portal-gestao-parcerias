from django.contrib import admin
from .models import Conciliacao, ImportacaoExtrato, Movimentacao, OcorrenciaConciliacao, VinculoConciliacao

admin.site.register(Conciliacao)
admin.site.register(ImportacaoExtrato)
admin.site.register(Movimentacao)
admin.site.register(VinculoConciliacao)
admin.site.register(OcorrenciaConciliacao)
