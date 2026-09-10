from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from apps.core.acesso import (
    empresa_do_usuario,
    filtrar_por_empresa,
    usuario_pode_ver_todas_empresas,
)
from apps.empresas.models import Empresa
from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos

from .forms import MovimentacaoFinanceiraForm
from .mixins import (
    MovimentacaoFinanceiraEscopoMixin,
    MovimentacaoFinanceiraPermissaoMixin,
)
from .conciliacao import resumo_conciliacao_competencia
from .models import MovimentacaoFinanceira
from .resumos import (
    resumo_financeiro_competencia,
    resumo_financeiro_competencias,
)


class MovimentacaoFinanceiraList(
    MovimentacaoFinanceiraPermissaoMixin,
    MovimentacaoFinanceiraEscopoMixin,
    ListView,
):
    model = MovimentacaoFinanceira
    template_name = (
        "financeiro/movimentacao_list.html"
    )
    context_object_name = "movimentacoes"
    permission_required = (
        "financeiro.view_movimentacaofinanceira"
    )
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related(
                "empresa",
                "termo",
                "prestacao",
                "competencia",
                "criado_por",
            )
        )

        empresa_id = (
            self.request.GET.get("empresa") or ""
        ).strip()

        termo_id = (
            self.request.GET.get("termo") or ""
        ).strip()

        prestacao_id = (
            self.request.GET.get("prestacao") or ""
        ).strip()

        competencia_id = (
            self.request.GET.get("competencia") or ""
        ).strip()

        tipo = (
            self.request.GET.get("tipo") or ""
        ).strip()

        if (
            empresa_id.isdigit()
            and usuario_pode_ver_todas_empresas(
                self.request.user
            )
        ):
            queryset = queryset.filter(
                empresa_id=empresa_id
            )

        if termo_id.isdigit():
            queryset = queryset.filter(
                termo_id=termo_id
            )

        if prestacao_id.isdigit():
            queryset = queryset.filter(
                prestacao_id=prestacao_id
            )

        if competencia_id.isdigit():
            queryset = queryset.filter(
                competencia_id=competencia_id
            )

        if tipo:
            queryset = queryset.filter(
                tipo=tipo
            )

        return queryset.order_by(
            "-data",
            "-id",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()

        context["empresa_filtro"] = (
            self.request.GET.get("empresa") or ""
        ).strip()

        context["termo_filtro"] = (
            self.request.GET.get("termo") or ""
        ).strip()

        context["prestacao_filtro"] = (
            self.request.GET.get("prestacao") or ""
        ).strip()

        context["competencia_filtro"] = (
            self.request.GET.get("competencia") or ""
        ).strip()

        context["tipo_filtro"] = (
            self.request.GET.get("tipo") or ""
        ).strip()

        context["tipos"] = (
            MovimentacaoFinanceira.Tipo.choices
        )

        context["total_movimentacoes"] = (
            queryset.count()
        )

        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if usuario_pode_ver_todas_empresas(
                self.request.user
            )
            else Empresa.objects.none()
        )

        pode_ver_todas = usuario_pode_ver_todas_empresas(
            self.request.user
        )

        context["pode_selecionar_empresa"] = pode_ver_todas

        empresa_resumo = None

        if pode_ver_todas:
            empresa_id = context["empresa_filtro"]

            if empresa_id.isdigit():
                empresa_resumo = (
                    Empresa.objects
                    .filter(pk=empresa_id)
                    .first()
                )
        else:
            empresa_resumo = empresa_do_usuario(
                self.request.user
            )

        context["empresa_resumo"] = empresa_resumo

        termos = Termos.objects.none()
        prestacoes = Prestacao.objects.none()
        competencias = CompetenciaPrestacao.objects.none()

        termo_resumo = None
        prestacao_resumo = None

        if empresa_resumo:
            termos = (
                Termos.objects
                .filter(empresa=empresa_resumo)
                .order_by("numtermo")
            )

            termo_id = context["termo_filtro"]

            if termo_id.isdigit():
                termo_resumo = (
                    termos
                    .filter(pk=termo_id)
                    .first()
                )

            if termo_resumo:
                prestacoes = (
                    Prestacao.objects
                    .filter(
                        empresa=empresa_resumo,
                        termo=termo_resumo,
                    )
                    .order_by("numtermo")
                )

            prestacao_id = context["prestacao_filtro"]

            if (
                termo_resumo
                and prestacao_id.isdigit()
            ):
                prestacao_resumo = (
                    prestacoes
                    .filter(pk=prestacao_id)
                    .first()
                )

            if prestacao_resumo:
                competencias = (
                    CompetenciaPrestacao.objects
                    .filter(
                        prestacao=prestacao_resumo,
                    )
                    .order_by("-ano", "-mes")
                )

        context["termo_resumo"] = termo_resumo
        context["prestacao_resumo"] = prestacao_resumo

        context["termos_disponiveis"] = termos
        context["prestacoes_disponiveis"] = prestacoes
        context["competencias_disponiveis"] = competencias

        competencia_resumo = None
        resumo_competencia = None

        competencia_id = context["competencia_filtro"]

        if competencia_id.isdigit():
            competencia_resumo = (
                competencias
                .filter(pk=competencia_id)
                .first()
            )

        resumo_conciliacao = None
        resumo_consolidado = None
        nivel_resumo = None
        objeto_resumo = None

        if competencia_resumo:
            resumo_competencia = (
                resumo_financeiro_competencia(
                    competencia_resumo
                )
            )

            resumo_conciliacao = (
                resumo_conciliacao_competencia(
                    competencia_resumo
                )
            )

        elif empresa_resumo:
            competencias_resumo = (
                CompetenciaPrestacao.objects
                .filter(
                    prestacao__empresa=empresa_resumo
                )
                .order_by(
                    "ano",
                    "mes",
                    "id",
                )
            )

            if prestacao_resumo:
                competencias_resumo = (
                    competencias_resumo
                    .filter(
                        prestacao=prestacao_resumo
                    )
                )

                nivel_resumo = "Prestacao"
                objeto_resumo = prestacao_resumo

            elif termo_resumo:
                competencias_resumo = (
                    competencias_resumo
                    .filter(
                        prestacao__termo=termo_resumo
                    )
                )

                nivel_resumo = "Termo"
                objeto_resumo = termo_resumo

            else:
                nivel_resumo = "Empresa"
                objeto_resumo = empresa_resumo

            resumo_consolidado = (
                resumo_financeiro_competencias(
                    competencias_resumo
                )
            )

        context["resumo_consolidado"] = (
            resumo_consolidado
        )
        context["nivel_resumo"] = nivel_resumo
        context["objeto_resumo"] = objeto_resumo

        context["competencia_resumo"] = (
            competencia_resumo
        )
        context["resumo_competencia"] = (
            resumo_competencia
        )
        context["resumo_conciliacao"] = (
            resumo_conciliacao
        )

        return context


class MovimentacaoFinanceiraCreate(
    MovimentacaoFinanceiraPermissaoMixin,
    CreateView,
):
    model = MovimentacaoFinanceira
    form_class = MovimentacaoFinanceiraForm
    template_name = (
        "financeiro/movimentacao_form.html"
    )
    permission_required = (
        "financeiro.add_movimentacaofinanceira"
    )
    success_url = reverse_lazy(
        "list_movimentacoes_financeiras"
    )

    def get_empresa_destino(self):
        if usuario_pode_ver_todas_empresas(
            self.request.user
        ):
            empresa_id = (
                self.request.GET.get("empresa")
                or self.request.POST.get("empresa")
            )

            if empresa_id:
                return (
                    Empresa.objects
                    .filter(pk=empresa_id)
                    .first()
                )

            return None

        return empresa_do_usuario(
            self.request.user
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["empresa"] = (
            self.get_empresa_destino()
        )

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["empresa_destino"] = (
            self.get_empresa_destino()
        )

        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if usuario_pode_ver_todas_empresas(
                self.request.user
            )
            else Empresa.objects.none()
        )

        return context

    def form_valid(self, form):
        empresa = self.get_empresa_destino()

        if not empresa:
            form.add_error(
                None,
                "Selecione uma empresa v?lida.",
            )
            return self.form_invalid(form)

        self.object = form.save(
            commit=False
        )

        self.object.empresa = empresa
        self.object.criado_por = (
            self.request.user
        )

        self.object.full_clean()
        self.object.save()

        messages.success(
            self.request,
            "Movimentação financeira cadastrada com sucesso.",
        )

        return HttpResponseRedirect(self.get_success_url())


class MovimentacaoFinanceiraUpdate(
    MovimentacaoFinanceiraPermissaoMixin,
    MovimentacaoFinanceiraEscopoMixin,
    UpdateView,
):
    model = MovimentacaoFinanceira
    form_class = MovimentacaoFinanceiraForm
    template_name = (
        "financeiro/movimentacao_form.html"
    )
    permission_required = (
        "financeiro.change_movimentacaofinanceira"
    )
    success_url = reverse_lazy(
        "list_movimentacoes_financeiras"
    )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["empresa"] = (
            self.object.empresa
        )

        return kwargs

    def form_valid(self, form):
        self.object = form.save(
            commit=False
        )

        self.object.full_clean()
        self.object.save()

        messages.success(
            self.request,
            "Movimentação financeira atualizada com sucesso.",
        )

        return HttpResponseRedirect(self.get_success_url())


class MovimentacaoFinanceiraDelete(
    MovimentacaoFinanceiraPermissaoMixin,
    MovimentacaoFinanceiraEscopoMixin,
    DeleteView,
):
    model = MovimentacaoFinanceira
    template_name = (
        "financeiro/movimentacao_confirm_delete.html"
    )
    context_object_name = "movimentacao"
    permission_required = (
        "financeiro.delete_movimentacaofinanceira"
    )
    success_url = reverse_lazy(
        "list_movimentacoes_financeiras"
    )


def _usuario_pode_consultar_financeiro(user):
    return (
        user.has_perm(
            "financeiro.view_movimentacaofinanceira"
        )
        or user.has_perm(
            "financeiro.add_movimentacaofinanceira"
        )
        or user.has_perm(
            "financeiro.change_movimentacaofinanceira"
        )
    )


def _validar_acesso_ajax_financeiro(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"detail": "Autenticação necessária."},
            status=401,
        )

    if not _usuario_pode_consultar_financeiro(
        request.user
    ):
        return JsonResponse(
            {"detail": "Sem permiss?o."},
            status=403,
        )

    return None


def termos_financeiro(request):
    resposta = _validar_acesso_ajax_financeiro(
        request
    )

    if resposta:
        return resposta

    empresa_id = (
        request.GET.get("empresa") or ""
    ).strip()

    termos = Termos.objects.all()

    if usuario_pode_ver_todas_empresas(
        request.user
    ):
        if not empresa_id.isdigit():
            return JsonResponse(
                {"termos": []}
            )

        termos = termos.filter(
            empresa_id=empresa_id
        )
    else:
        empresa = empresa_do_usuario(
            request.user
        )

        if not empresa:
            return JsonResponse(
                {"termos": []}
            )

        termos = termos.filter(
            empresa=empresa
        )

    dados = [
        {
            "id": item.pk,
            "texto": str(item),
        }
        for item in termos.order_by(
            "numtermo"
        )
    ]

    return JsonResponse(
        {"termos": dados}
    )


def prestacoes_financeiro(request):
    resposta = _validar_acesso_ajax_financeiro(
        request
    )

    if resposta:
        return resposta

    termo_id = (
        request.GET.get("termo") or ""
    ).strip()

    if not termo_id.isdigit():
        return JsonResponse(
            {"prestacoes": []}
        )

    queryset = Prestacao.objects.filter(
        termo_id=termo_id
    )

    queryset = filtrar_por_empresa(
        queryset,
        request.user,
        campo="empresa",
    )

    dados = [
        {
            "id": item.pk,
            "texto": str(item),
        }
        for item in queryset.order_by(
            "numtermo"
        )
    ]

    return JsonResponse(
        {"prestacoes": dados}
    )


def competencias_financeiro(request):
    resposta = _validar_acesso_ajax_financeiro(
        request
    )

    if resposta:
        return resposta

    prestacao_id = (
        request.GET.get("prestacao") or ""
    ).strip()

    if not prestacao_id.isdigit():
        return JsonResponse(
            {"competencias": []}
        )

    queryset = (
        CompetenciaPrestacao.objects
        .filter(
            prestacao_id=prestacao_id
        )
    )

    queryset = filtrar_por_empresa(
        queryset,
        request.user,
        campo="prestacao__empresa",
    )

    dados = [
        {
            "id": item.pk,
            "texto": str(item),
        }
        for item in queryset.order_by(
            "-ano",
            "-mes",
        )
    ]

    return JsonResponse(
        {"competencias": dados}
    )
