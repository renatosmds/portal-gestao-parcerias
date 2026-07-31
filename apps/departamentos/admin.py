from django.contrib import admin

from .models import Departamento


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "empresa", "total_funcionarios")
    list_filter = ("empresa",)
    search_fields = ("nome", "empresa__nome")
    ordering = ("empresa__nome", "nome")
    autocomplete_fields = ("empresa",)

    @admin.display(description="Funcionários")
    def total_funcionarios(self, obj):
        return obj.funcionario_set.count()
