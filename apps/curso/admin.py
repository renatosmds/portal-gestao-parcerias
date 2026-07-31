from django.contrib import admin
from .models import Curso


class CursoAdmin(admin.ModelAdmin):
    list_display = ['nomeCurso', 'anoCurso', 'mesCurso', 'cronograma', 'horario', 'carga', 'obs'
                    ]

    fieldsets = (
        ('DADOS GERAIS', {
            'classes': ('collapse',),
            'fields': (('nomeCurso'), ('anoCurso', 'mesCurso'), ('cronograma', 'horario'), ('carga', 'docente'))}),

        ('DADOS COMPLEMENTARES', {
            'classes': ('collapse',),
            'fields': (('ementa'), ('obs'), ('certificado', 'documento'),
                       )}),
    )

admin.site.register(Curso, CursoAdmin)