from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.empresas.models import Empresa

from .forms import DepartamentoForm
from .mixins import DepartamentoEscopoMixin, DepartamentoPermissaoMixin
from .models import Departamento


def _montar_organograma_texto(unidades):
    unidades = list(unidades)

    if not unidades:
        return ""

    ids = {
        unidade.pk
        for unidade in unidades
    }

    filhos = {}

    for unidade in unidades:
        pai_id = unidade.superior_id

        if pai_id not in ids:
            pai_id = None

        filhos.setdefault(
            pai_id,
            [],
        ).append(unidade)

    ordem_tipos = {
        Departamento.Tipo.DEPARTAMENTO: 0,
        Departamento.Tipo.GABINETE: 1,
        Departamento.Tipo.ASSESSORIA: 2,
        Departamento.Tipo.SUPERINTENDENCIA: 3,
        Departamento.Tipo.SUBSECRETARIA: 4,
        Departamento.Tipo.DIRETORIA: 5,
        Departamento.Tipo.GERENCIA: 6,
    }

    for lista in filhos.values():
        lista.sort(
            key=lambda unidade: (
                ordem_tipos.get(
                    unidade.tipo,
                    99,
                ),
                unidade.nome.casefold(),
            )
        )

    linhas = []

    def adicionar(unidade, prefixo="", ultimo=True, raiz=False):
        if raiz:
            prefixo_visual = ""
        else:
            conector = (
                "\u2514\u2500\u2500 "
                if ultimo
                else "\u251c\u2500\u2500 "
            )
            prefixo_visual = f"{prefixo}{conector}"

        linhas.append(
            {
                "pk": unidade.pk,
                "nome": unidade.nome,
                "prefixo": prefixo_visual,
            }
        )

        subunidades = filhos.get(
            unidade.pk,
            [],
        )

        if raiz:
            novo_prefixo = ""
        else:
            novo_prefixo = (
                prefixo
                + ("    " if ultimo else "\u2502   ")
            )

        for indice, subunidade in enumerate(subunidades):
            adicionar(
                subunidade,
                prefixo=novo_prefixo,
                ultimo=(
                    indice
                    == len(subunidades) - 1
                ),
            )

    raizes = filhos.get(None, [])

    for raiz in raizes:
        adicionar(
            raiz,
            raiz=True,
        )

    return linhas


class DepartamentosList(
    DepartamentoPermissaoMixin,
    DepartamentoEscopoMixin,
    ListView,
):
    model = Departamento
    template_name = "departamentos/departamento_list.html"
    context_object_name = "departamentos"
    permission_required = "departamentos.view_departamento"
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        termo = (self.request.GET.get("q") or "").strip()
        empresa_id = (self.request.GET.get("empresa") or "").strip()

        if termo:
            queryset = queryset.filter(nome__icontains=termo)

        if empresa_id and self.request.user.is_superuser:
            queryset = queryset.filter(empresa_id=empresa_id)

        return queryset.annotate(
            quantidade_funcionarios=Count("funcionario", distinct=True),
            quantidade_ativos=Count(
                "funcionario",
                filter=Q(funcionario__ativo=True),
                distinct=True,
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["termo_busca"] = (self.request.GET.get("q") or "").strip()
        context["empresa_filtro"] = (self.request.GET.get("empresa") or "").strip()
        queryset_contexto = self.get_queryset()

        context["total_departamentos"] = queryset_contexto.count()

        empresas_ids = list(
            queryset_contexto
            .order_by()
            .values_list(
                "empresa_id",
                flat=True,
            )
            .distinct()[:2]
        )

        context["organograma_linhas"] = []
        context["organograma_disponivel"] = False

        if len(empresas_ids) == 1:
            unidades_organograma = (
                Departamento.objects
                .filter(
                    empresa_id=empresas_ids[0],
                )
                .select_related(
                    "superior",
                    "empresa",
                )
            )

            context["organograma_linhas"] = (
                _montar_organograma_texto(
                    unidades_organograma
                )
            )

            context["organograma_disponivel"] = True

        context["organograma_multiplas_empresas"] = (
            len(empresas_ids) > 1
        )

        if self.request.user.is_superuser:
            context["empresas_disponiveis"] = Empresa.objects.order_by("nome")
        else:
            context["empresas_disponiveis"] = Empresa.objects.none()

        return context


class DepartamentoDetail(
    DepartamentoPermissaoMixin,
    DepartamentoEscopoMixin,
    DetailView,
):
    model = Departamento
    template_name = "departamentos/departamento_detail.html"
    context_object_name = "departamento"
    permission_required = "departamentos.view_departamento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        funcionarios = self.object.funcionario_set.all().order_by("nome")
        context["funcionarios"] = funcionarios[:12]
        context["total_funcionarios"] = funcionarios.count()
        context["total_ativos"] = funcionarios.filter(ativo=True).count()
        context["total_ferias"] = funcionarios.filter(de_ferias=True).count()

        subunidades = (
            self.object.subunidades
            .all()
            .order_by("tipo", "nome")
        )

        context["subunidades"] = subunidades
        context["total_subunidades"] = subunidades.count()

        return context


class DepartamentoCreate(
    DepartamentoPermissaoMixin,
    CreateView,
):
    model = Departamento
    form_class = DepartamentoForm
    template_name = "departamentos/departamento_form.html"
    permission_required = "departamentos.add_departamento"

    def get_empresa_destino(self):
        if self.request.user.is_superuser:
            empresa_id = self.request.GET.get("empresa") or self.request.POST.get("empresa")
            if empresa_id:
                return Empresa.objects.filter(pk=empresa_id).first()
            return None

        try:
            return self.request.user.funcionario.empresa
        except Exception:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.get_empresa_destino()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresa_destino"] = self.get_empresa_destino()
        context["empresas_disponiveis"] = (
            Empresa.objects.order_by("nome")
            if self.request.user.is_superuser
            else Empresa.objects.none()
        )
        return context

    def form_valid(self, form):
        empresa = self.get_empresa_destino()

        if not empresa:
            form.add_error(
                None,
                "Selecione uma empresa válida para o departamento.",
            )
            return self.form_invalid(form)

        departamento = form.save(commit=False)
        departamento.empresa = empresa
        departamento.save()
        self.object = departamento

        messages.success(
            self.request,
            f"Departamento “{departamento.nome}” cadastrado com sucesso.",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "detail_departamento",
            kwargs={"pk": self.object.pk},
        )


class DepartamentoUpdate(
    DepartamentoPermissaoMixin,
    DepartamentoEscopoMixin,
    UpdateView,
):
    model = Departamento
    form_class = DepartamentoForm
    template_name = "departamentos/departamento_form.html"
    permission_required = "departamentos.change_departamento"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["empresa"] = self.object.empresa
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["empresa_destino"] = self.object.empresa
        context["empresas_disponiveis"] = Empresa.objects.none()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Departamento “{self.object.nome}” atualizado com sucesso.",
        )
        return response

    def get_success_url(self):
        return reverse_lazy(
            "detail_departamento",
            kwargs={"pk": self.object.pk},
        )


class DepartamentoDelete(
    DepartamentoPermissaoMixin,
    DepartamentoEscopoMixin,
    DeleteView,
):
    model = Departamento
    template_name = "departamentos/departamento_confirm_delete.html"
    context_object_name = "departamento"
    permission_required = "departamentos.delete_departamento"
    success_url = reverse_lazy("list_departamentos")

    def form_valid(self, form):
        nome = self.object.nome
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Departamento “{nome}” excluído com sucesso.",
        )
        return response
