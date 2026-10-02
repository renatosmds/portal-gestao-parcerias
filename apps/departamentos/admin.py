from django.contrib import admin

from .models import Departamento


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "tipo",
        "superior",
        "empresa",
        "total_funcionarios",
    )

    list_filter = (
        "empresa",
        "tipo",
    )

    search_fields = (
        "nome",
        "empresa__nome",
        "superior__nome",
    )

    ordering = (
        "empresa__nome",
        "tipo",
        "nome",
    )

    autocomplete_fields = (
        "empresa",
        "superior",
    )

    @admin.display(description="Funcionarios")
    def total_funcionarios(self, obj):
        return obj.funcionario_set.count()
