from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.template.response import TemplateResponse

from .models import ConciliacaoFinanceira, ImportacaoOFX


@admin.register(ImportacaoOFX)
class ImportacaoOFXAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nome_arquivo",
        "empresa",
        "termo",
        "prestacao",
        "quantidade_movimentos",
        "importado_por",
        "importado_em",
    )

    list_filter = (
        "empresa",
        "termo",
        "importado_em",
    )

    search_fields = (
        "nome_arquivo",
        "termo__numtermo",
        "prestacao__numtermo",
    )

    readonly_fields = (
        "empresa",
        "termo",
        "prestacao",
        "nome_arquivo",
        "hash_arquivo",
        "banco",
        "conta_mascarada",
        "tipo_conta",
        "moeda",
        "data_inicio",
        "data_fim",
        "saldo_informado",
        "data_saldo",
        "quantidade_movimentos",
        "importado_por",
        "importado_em",
    )

    actions = (
        "desfazer_importacao_ofx",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return request.user.is_superuser

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)

        if not request.user.is_superuser:
            actions.pop(
                "desfazer_importacao_ofx",
                None,
            )

        return actions

    @admin.action(
        description=(
            "Desfazer importacao OFX selecionada"
        )
    )
    def desfazer_importacao_ofx(
        self,
        request,
        queryset,
    ):
        if not request.user.is_superuser:
            self.message_user(
                request,
                "Operacao permitida somente "
                "para superusuario.",
                level=messages.ERROR,
            )
            return

        if queryset.count() != 1:
            self.message_user(
                request,
                "Selecione exatamente uma importacao OFX.",
                level=messages.ERROR,
            )
            return

        importacao = queryset.first()

        quantidade = (
            importacao.movimentos.count()
        )

        possui_conciliacao = (
            ConciliacaoFinanceira.objects.filter(
                movimentacao__importacao_ofx=importacao
            ).exists()
        )

        if possui_conciliacao:
            self.message_user(
                request,
                (
                    "A importacao nao pode ser desfeita "
                    "porque existem conciliacoes manuais "
                    "associadas aos movimentos."
                ),
                level=messages.ERROR,
            )
            return

        if request.POST.get("confirmar") != "sim":
            contexto = {
                **self.admin_site.each_context(request),
                "title": "Confirmar desfazer importacao OFX",
                "opts": self.model._meta,
                "importacao": importacao,
                "quantidade": quantidade,
                "queryset": queryset,
                "action_checkbox_name": (
                    helpers.ACTION_CHECKBOX_NAME
                ),
            }

            return TemplateResponse(
                request,
                (
                    "admin/financeiro/importacaoofx/"
                    "confirmar_desfazer.html"
                ),
                contexto,
            )

        try:
            with transaction.atomic():
                importacao.movimentos.all().delete()
                importacao.delete()

        except ProtectedError:
            self.message_user(
                request,
                (
                    "A importacao nao pode ser desfeita "
                    "porque existem registros protegidos "
                    "relacionados aos movimentos."
                ),
                level=messages.ERROR,
            )
            return

        self.message_user(
            request,
            (
                "Importacao OFX desfeita com sucesso. "
                f"Movimentos removidos: {quantidade}."
            ),
            level=messages.SUCCESS,
        )
