from django.contrib import admin
from .models import RegistroHoraExtra


class RegistroHoraExtraAdmin(admin.ModelAdmin):
    list_display = ['funcionario', 'motivo', 'horas', 'assunto']

    fieldsets = (
        ('Dados Gerais', {'fields': ('funcionario', 'horas',)}),
        ('Dados Complementares', {
            'classes': ('collapse',),
            'fields': ['motivo', 'assunto']
        }
         )
    )


admin.site.register(RegistroHoraExtra, RegistroHoraExtraAdmin)
