from django.contrib import admin

from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nome", "total_funcionarios")
    search_fields = ("nome",)
    ordering = ("nome",)

    @admin.display(description="Funcionários")
    def total_funcionarios(self, obj):
        return obj.funcionario_set.count()
