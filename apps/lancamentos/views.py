from django.contrib import messages
from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.http import JsonResponse

from apps.empresas.models import Empresa
from apps.prestacao.models import CompetenciaPrestacao, Prestacao
from apps.core.acesso import empresa_do_usuario, usuario_pode_ver_todas_empresas

from .forms import GlosaLancamentoForm, LancamentoForm
from .mixins import LancamentoEscopoMixin, LancamentoPermissaoMixin
from .models import HistoricoGlosa, Lancamento



def prestacoes_por_termo(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"detail": "Autenticacao necessaria."},
            status=401,
        )

    if not (
        request.user.has_perm("lancamentos.add_lancamento")
        or request.user.has_perm("lancamentos.change_lancamento")
    ):
        return JsonResponse(
            {"detail": "Sem permissao."},
            status=403,
        )

    termo_id = (
        request.GET.get("termo") or ""
    ).strip()

    if not termo_id.isdigit():
        return JsonResponse({"prestacoes": []})

    prestacoes = (
        Prestacao.objects
        .filter(termo_id=termo_id)
        .select_related("empresa", "termo")
        .order_by("numtermo", "credor")
    )

    if not usuario_pode_ver_todas_empresas(request.user):
        try:
            empresa = empresa_do_usuario(request.user)
        except Exception:
            empresa = None

        if empresa:
            prestacoes = prestacoes.filter(
                empresa=empresa
            )
        else:
            prestacoes = prestacoes.none()

    dados = [
        {
            "id": prestacao.pk,
            "texto": str(prestacao),
        }
        for prestacao in prestacoes
    ]

    return JsonResponse({"prestacoes": dados})


def competencias_por_prestacao(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"detail": "Autenticacao necessaria."},
            status=401,
        )

    if not (
        request.user.has_perm("lancamentos.add_lancamento")
        or request.user.has_perm("lancamentos.change_lancamento")
    ):
        return JsonResponse(
            {"detail": "Sem permissao."},
            status=403,
        )

    prestacao_id = (
        request.GET.get("prestacao") or ""
    ).strip()

    if not prestacao_id.isdigit():
        return JsonResponse({"competencias": []})

    competencias = (
        CompetenciaPrestacao.objects
        .filter(prestacao_id=prestacao_id)
        .select_related(
            "prestacao",
            "prestacao__empresa",
        )
        .order_by("-ano", "-mes")
    )

    if not usuario_pode_ver_todas_empresas(request.user):
        try:
            empresa = empresa_do_usuario(request.user)
        except Exception:
            empresa = None

        if empresa:
            competencias = competencias.filter(
                prestacao__empresa=empresa
            )
        else:
            competencias = competencias.none()

    dados = [
        {
            "id": competencia.pk,
            "texto": str(competencia),
        }
        for competencia in competencias
    ]

    return JsonResponse({"competencias": dados})


class LancamentoList(
    LancamentoPermissaoMixin,
    LancamentoEscopoMixin,
    ListView,
):
    model = Lancamento
    template_name = "lancamentos/lancamento_list.html"
    context_object_name = "lancamentos"
    permission_required = "lancamentos.view_lancamento"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = (self.request.GET.get("q") or "").strip()
        situacao = (self.request.GET.get("situacao") or "").strip()
        empresa_id = (self.request.GET.get("empresa") or "").strip()
        competencia_id = (
            self.request.GET.get("competencia") or ""
        ).strip()

        if busca:
            queryset = queryset.filter(
                Q(numero_lancamento__icontains=busca)
                | Q(numero_documento__icontains=busca)
                | Q(chave_acesso__icontains=busca)
                | Q(descricao__icontains=busca)
                | Q(fornecedor__credor__icontains=busca)
                | Q(fornecedor__razao__icontains=busca)
                | Q(fornecedor__fantasia__icontains=busca)
                | Q(termo__termo__icontains=busca)
                | Q(termo__numtermo__icontains=busca)
                | Q(prestacao__numtermo__icontains=busca)
            )

        if situacao:
            queryset = queryset.filter(situacao=situacao)

        if empresa_id and usuario_pode_ver_todas_empresas(self.request.user):
            queryset = queryset.filter(empresa_id=empresa_id)

        if competencia_id.isdigit():
            queryset = queryset.filter(
                competencia_id=competencia_id
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        totais = queryset.aggregate(
            total_documentos=Coalesce(
                Sum("valor_documento"),
                Value(0),
                output_field=DecimalField(max_digits=15, decimal_places=2),
            ),
            total_glosas=Coalesce(
                Sum("valor_glosa"),
                Value(0),
                output_field=DecimalField(max_digits=15, decimal_places=2),
            ),
        )
        context.update(totais)
        context["total_lancamentos"] = queryset.count()
        context["busca"] = (self.request.GET.get("q") or "").strip()
        context["situacao_filtro"] = (
            self.request.GET.get("situacao") or ""
        ).strip()
        context["empresa_filtro"] = (
            self.request.GET.get("empresa") or ""
        ).strip()
        context["competencia_filtro"] = (
            self.request.GET.get("competencia") or ""
        ).strip()
        context["situacoes"] = Lancamento.Situacao.choices
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if usuario_pode_ver_todas_empresas(self.request.user)
            else Empresa.objects.none()
        )

        competencias = CompetenciaPrestacao.objects.select_related(
            "prestacao",
            "prestacao__empresa",
        ).order_by("-ano", "-mes", "prestacao__numtermo")

        empresa_filtro = context["empresa_filtro"]

        if empresa_filtro.isdigit() and usuario_pode_ver_todas_empresas(
            self.request.user
        ):
            competencias = competencias.filter(
                prestacao__empresa_id=empresa_filtro
            )
        elif not usuario_pode_ver_todas_empresas(self.request.user):
            try:
                empresa = empresa_do_usuario(self.request.user)
            except Exception:
                empresa = None

            if empresa:
                competencias = competencias.filter(
                    prestacao__empresa=empresa
                )
            else:
                competencias = competencias.none()

        context["competencias_disponiveis"] = competencias

        competencia_selecionada = None
        competencia_id = context["competencia_filtro"]

        if competencia_id.isdigit():
            competencia_selecionada = (
                competencias.filter(pk=competencia_id).first()
            )

        context["competencia_selecionada"] = competencia_selecionada

        if competencia_selecionada:
            resumo = (
                Lancamento.objects.filter(
                    competencia=competencia_selecionada
                )
                .aggregate(
                    qtd=Count("id"),
                    regulares=Count(
                        "id",
                        filter=Q(
                            situacao=Lancamento.Situacao.REGULAR
                        ),
                    ),
                    ressalvas=Count(
                        "id",
                        filter=Q(
                            situacao=Lancamento.Situacao.RESSALVA
                        ),
                    ),
                    glosados=Count(
                        "id",
                        filter=Q(
                            situacao=Lancamento.Situacao.GLOSADO
                        ),
                    ),
                    nao_analisados=Count(
                        "id",
                        filter=Q(
                            situacao=Lancamento.Situacao.NAO_ANALISADO
                        ),
                    ),
                    total_documentos=Sum("valor_documento"),
                    total_glosas=Sum("valor_glosa"),
                )
            )

            total_documentos = resumo["total_documentos"] or 0
            total_glosas = resumo["total_glosas"] or 0
            total_aprovado = total_documentos - total_glosas

            context["competencia_qtd_lancamentos"] = resumo["qtd"]
            context["competencia_regulares"] = resumo["regulares"]
            context["competencia_ressalvas"] = resumo["ressalvas"]
            context["competencia_glosados"] = resumo["glosados"]
            context["competencia_nao_analisados"] = resumo["nao_analisados"]
            context["competencia_total_documentos"] = total_documentos
            context["competencia_total_glosas"] = total_glosas
            context["competencia_total_aprovado"] = total_aprovado

            if total_documentos:
                context["competencia_percentual_aprovado"] = (
                    total_aprovado * 100 / total_documentos
                )
            else:
                context["competencia_percentual_aprovado"] = 0

        return context


class LancamentoDetail(
    LancamentoPermissaoMixin,
    LancamentoEscopoMixin,
    DetailView,
):
    model = Lancamento
    template_name = "lancamentos/lancamento_detail.html"
    context_object_name = "lancamento"
    permission_required = "lancamentos.view_lancamento"

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context["historico_glosas"] = self.object.historico_glosas.select_related("usuario")[:20]
        return context


class LancamentoCreate(LancamentoPermissaoMixin, CreateView):
    model = Lancamento
    form_class = LancamentoForm
    template_name = "lancamentos/lancamento_form.html"
    permission_required = "lancamentos.add_lancamento"

    def get_empresa_destino(self):
        if usuario_pode_ver_todas_empresas(self.request.user):
            empresa_id = (
                self.request.GET.get("empresa")
                or self.request.POST.get("empresa")
            )
            return (
                Empresa.objects.filter(pk=empresa_id).first()
                if empresa_id
                else None
            )
        try:
            return empresa_do_usuario(self.request.user)
        except Exception:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa_destino()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if usuario_pode_ver_todas_empresas(self.request.user)
            else Empresa.objects.none()
        )
        return context

    def form_valid(self, form):
        empresa = self.get_empresa_destino()
        if not empresa:
            form.add_error(
                None,
                "Selecione uma empresa válida para o lançamento.",
            )
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.empresa = empresa
        self.object.criado_por = self.request.user
        self.object.save()

        messages.success(
            self.request,
            f"Lançamento “{self.object}” cadastrado com sucesso.",
        )
        return super().form_valid(form)


class LancamentoUpdate(
    LancamentoPermissaoMixin,
    LancamentoEscopoMixin,
    UpdateView,
):
    model = Lancamento
    form_class = LancamentoForm
    template_name = "lancamentos/lancamento_form.html"
    permission_required = "lancamentos.change_lancamento"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.object.empresa
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Lançamento “{self.object}” atualizado com sucesso.",
        )
        return response


class LancamentoDelete(
    LancamentoPermissaoMixin,
    LancamentoEscopoMixin,
    DeleteView,
):
    model = Lancamento
    template_name = "lancamentos/lancamento_confirm_delete.html"
    context_object_name = "lancamento"
    permission_required = "lancamentos.delete_lancamento"
    success_url = reverse_lazy("list_lancamentos")


@login_required
@permission_required("lancamentos.change_lancamento", raise_exception=True)
def registrar_glosa(request, pk):
    lancamento=get_object_or_404(Lancamento, pk=pk)
    anterior_tipo=lancamento.tipo_glosa; anterior_valor=lancamento.valor_glosa
    form=GlosaLancamentoForm(request.POST or None, instance=lancamento)
    if request.method == "POST" and form.is_valid():
        obj=form.save(commit=False)
        if obj.tipo_glosa == Lancamento.TipoGlosa.NENHUMA:
            obj.valor_glosa=0; obj.situacao=Lancamento.Situacao.REGULAR; obj.motivo_glosa=""; obj.fundamentacao_glosa=""
        else:
            obj.situacao=Lancamento.Situacao.GLOSADO
        obj.glosa_registrada_por=request.user; obj.glosa_registrada_em=timezone.now(); obj.save()
        HistoricoGlosa.objects.create(lancamento=obj, tipo_anterior=anterior_tipo, tipo_novo=obj.tipo_glosa, valor_anterior=anterior_valor, valor_novo=obj.valor_glosa, motivo=obj.motivo_glosa, fundamentacao=obj.fundamentacao_glosa, usuario=request.user)
        messages.success(request, "Glosa registrada e valores recalculados.")
        return redirect("detail_lancamento", pk=obj.pk)
    return render(request, "lancamentos/lancamento_glosa_form.html", {"lancamento":lancamento, "form":form})
