from tempfile import NamedTemporaryFile
from pathlib import Path
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
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
from apps.lancamentos.models import Lancamento
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
from .conciliacao import (
    buscar_candidatos_lancamento,
    diagnostico_conciliacao_competencia,
    resumo_conciliacao_competencia,
)
from .models import (
    ConciliacaoFinanceira,
    MovimentacaoFinanceira,
)
from .servicos_ofx import importar_ofx

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
        diagnostico_conciliacao = None
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

            diagnostico_conciliacao = (
                diagnostico_conciliacao_competencia(
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

        context["diagnostico_conciliacao"] = (
            diagnostico_conciliacao
        )

        context["pode_decidir_conciliacao"] = (
            self.request.user.has_perm(
                "financeiro.change_movimentacaofinanceira"
            )
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



@login_required
@permission_required(
    "financeiro.add_movimentacaofinanceira",
    raise_exception=True,
)
@require_POST
def importar_ofx_financeiro(request):
    empresa_id = (
        request.POST.get("empresa") or ""
    ).strip()

    termo_id = (
        request.POST.get("termo") or ""
    ).strip()

    prestacao_id = (
        request.POST.get("prestacao") or ""
    ).strip()

    competencia_id = (
        request.POST.get("competencia") or ""
    ).strip()

    arquivo = request.FILES.get(
        "arquivo_ofx"
    )

    if usuario_pode_ver_todas_empresas(
        request.user
    ):
        if not empresa_id.isdigit():
            messages.error(
                request,
                "Selecione uma empresa valida.",
            )
            return HttpResponseRedirect(
                reverse_lazy(
                    "list_movimentacoes_financeiras"
                )
            )

        empresa = (
            Empresa.objects
            .filter(pk=empresa_id)
            .first()
        )
    else:
        empresa = empresa_do_usuario(
            request.user
        )

    if not empresa:
        messages.error(
            request,
            "Empresa nao encontrada ou sem acesso.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    if not termo_id.isdigit():
        messages.error(
            request,
            "Selecione um termo valido.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    termo = (
        Termos.objects
        .filter(
            pk=termo_id,
            empresa=empresa,
        )
        .first()
    )

    if not termo:
        messages.error(
            request,
            "O termo nao pertence a empresa selecionada.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    if not prestacao_id.isdigit():
        messages.error(
            request,
            "Selecione uma prestacao valida.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    prestacao = (
        Prestacao.objects
        .filter(
            pk=prestacao_id,
            empresa=empresa,
            termo=termo,
        )
        .first()
    )

    if not prestacao:
        messages.error(
            request,
            "A prestacao nao pertence ao termo selecionado.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    if not competencia_id.isdigit():
        messages.error(
            request,
            "Selecione uma competencia valida.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    competencia = (
        CompetenciaPrestacao.objects
        .filter(
            pk=competencia_id,
            prestacao=prestacao,
        )
        .first()
    )

    if not competencia:
        messages.error(
            request,
            "A competencia nao pertence "
            "a prestacao selecionada.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    if arquivo is None:
        messages.error(
            request,
            "Selecione um arquivo OFX.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    nome_arquivo = (
        arquivo.name or ""
    )

    if not nome_arquivo.lower().endswith(".ofx"):
        messages.error(
            request,
            "O arquivo deve possuir extensao .ofx.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    if arquivo.size > 5 * 1024 * 1024:
        messages.error(
            request,
            "O arquivo OFX excede o limite de 5 MB.",
        )
        return HttpResponseRedirect(
            reverse_lazy(
                "list_movimentacoes_financeiras"
            )
        )

    caminho_temporario = None

    try:
        with NamedTemporaryFile(
            suffix=".ofx",
            delete=False,
        ) as temporario:
            for bloco_arquivo in arquivo.chunks():
                temporario.write(bloco_arquivo)

            caminho_temporario = Path(
                temporario.name
            )

        importacao, criada = importar_ofx(
            caminho_temporario,
            empresa=empresa,
            termo=termo,
            prestacao=prestacao,
            competencia=competencia,
            usuario=request.user,
        )

        lidos = (
            importacao.quantidade_movimentos
        )

        if criada:
            importados = (
                importacao.movimentos.count()
            )

            duplicados = max(
                lidos - importados,
                0,
            )

            messages.success(
                request,
                (
                    "OFX importado com sucesso. "
                    f"Movimentos lidos: {lidos}. "
                    f"Novos: {importados}. "
                    f"Duplicados ignorados: {duplicados}."
                ),
            )
        else:
            messages.info(
                request,
                (
                    "Este arquivo OFX ja havia sido importado. "
                    f"Movimentos reconhecidos: {lidos}."
                ),
            )

    except ValidationError as exc:
        messages.error(
            request,
            "Nao foi possivel importar o OFX: "
            f"{exc}",
        )

    except (ValueError, UnicodeError) as exc:
        messages.error(
            request,
            "Arquivo OFX invalido: "
            f"{exc}",
        )

    except Exception:
        messages.error(
            request,
            "Nao foi possivel processar o arquivo OFX.",
        )

    finally:
        if (
            caminho_temporario
            and caminho_temporario.exists()
        ):
            caminho_temporario.unlink()

    destino = (
        reverse_lazy(
            "list_movimentacoes_financeiras"
        )
        + f"?empresa={empresa.pk}"
        + f"&termo={termo.pk}"
        + f"&prestacao={prestacao.pk}"
        + f"&competencia={competencia.pk}"
    )

    return HttpResponseRedirect(
        destino
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


def _movimentacao_financeira_do_usuario(
    user,
    movimentacao_id,
):
    queryset = (
        MovimentacaoFinanceira.objects
        .select_related(
            "empresa",
            "termo",
            "prestacao",
            "competencia",
        )
    )

    queryset = filtrar_por_empresa(
        queryset,
        user,
        campo="empresa",
    )

    return get_object_or_404(
        queryset,
        pk=movimentacao_id,
    )


def _lancamento_candidato_da_movimentacao(
    movimentacao,
    lancamento_id,
):
    resultado = buscar_candidatos_lancamento(
        movimentacao
    )

    candidatos_ids = {
        candidato.pk
        for candidato in resultado["candidatos"]
    }

    if lancamento_id not in candidatos_ids:
        return None

    return get_object_or_404(
        Lancamento.objects.filter(
            empresa_id=movimentacao.empresa_id,
            termo_id=movimentacao.termo_id,
            prestacao_id=movimentacao.prestacao_id,
            competencia_id=movimentacao.competencia_id,
        ),
        pk=lancamento_id,
    )


def _retorno_conciliacao(request):
    destino = (
        request.POST.get("next") or ""
    ).strip()

    if (
        destino
        and url_has_allowed_host_and_scheme(
            url=destino,
            allowed_hosts={
                request.get_host()
            },
            require_https=request.is_secure(),
        )
    ):
        return destino

    return reverse_lazy(
        "list_movimentacoes_financeiras"
    )


@login_required
@permission_required(
    "financeiro.change_movimentacaofinanceira",
    raise_exception=True,
)
@require_POST
def confirmar_conciliacao_financeira(
    request,
    movimentacao_id,
    lancamento_id,
):
    movimentacao = (
        _movimentacao_financeira_do_usuario(
            request.user,
            movimentacao_id,
        )
    )

    lancamento = (
        _lancamento_candidato_da_movimentacao(
            movimentacao,
            lancamento_id,
        )
    )

    if lancamento is None:
        messages.error(
            request,
            "O lancamento informado nao e candidato "
            "para esta movimentacao.",
        )

        return HttpResponseRedirect(
            _retorno_conciliacao(request)
        )

    conciliacao, _ = (
        ConciliacaoFinanceira.objects
        .get_or_create(
            movimentacao=movimentacao,
            defaults={
                "lancamento": lancamento,
                "status": (
                    ConciliacaoFinanceira.Status
                    .CONFIRMADO
                ),
                "decidido_por": request.user,
            },
        )
    )

    conciliacao.lancamento = lancamento
    conciliacao.status = (
        ConciliacaoFinanceira.Status.CONFIRMADO
    )
    conciliacao.decidido_por = request.user

    try:
        conciliacao.full_clean()
        conciliacao.save()

    except ValidationError as exc:
        messages.error(
            request,
            "Nao foi possivel confirmar a conciliacao: "
            f"{exc}",
        )

        return HttpResponseRedirect(
            _retorno_conciliacao(request)
        )

    messages.success(
        request,
        "Conciliacao confirmada com sucesso.",
    )

    return HttpResponseRedirect(
        _retorno_conciliacao(request)
    )


@login_required
@permission_required(
    "financeiro.change_movimentacaofinanceira",
    raise_exception=True,
)
@require_POST
def rejeitar_conciliacao_financeira(
    request,
    movimentacao_id,
    lancamento_id,
):
    movimentacao = (
        _movimentacao_financeira_do_usuario(
            request.user,
            movimentacao_id,
        )
    )

    lancamento = (
        _lancamento_candidato_da_movimentacao(
            movimentacao,
            lancamento_id,
        )
    )

    if lancamento is None:
        messages.error(
            request,
            "O lancamento informado nao e candidato "
            "para esta movimentacao.",
        )

        return HttpResponseRedirect(
            _retorno_conciliacao(request)
        )

    conciliacao, _ = (
        ConciliacaoFinanceira.objects
        .get_or_create(
            movimentacao=movimentacao,
            defaults={
                "lancamento": lancamento,
                "status": (
                    ConciliacaoFinanceira.Status
                    .REJEITADO
                ),
                "decidido_por": request.user,
            },
        )
    )

    conciliacao.lancamento = lancamento
    conciliacao.status = (
        ConciliacaoFinanceira.Status.REJEITADO
    )
    conciliacao.decidido_por = request.user

    try:
        conciliacao.full_clean()
        conciliacao.save()

    except ValidationError as exc:
        messages.error(
            request,
            "Nao foi possivel rejeitar a conciliacao: "
            f"{exc}",
        )

        return HttpResponseRedirect(
            _retorno_conciliacao(request)
        )

    messages.success(
        request,
        "Correspondencia rejeitada.",
    )

    return HttpResponseRedirect(
        _retorno_conciliacao(request)
    )
