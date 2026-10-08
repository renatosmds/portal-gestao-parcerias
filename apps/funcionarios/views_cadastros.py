from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from .forms import (
    CargoForm,
    EquipamentoForm,
    NivelForm,
)
from .models import (
    Cargo,
    Equipamento,
    Nivel,
)
from apps.empresas.models import Empresa

from .services import get_empresa_do_usuario


class CadastroAuxiliarMixin(
    LoginRequiredMixin,
    PermissionRequiredMixin,
):
    empresa_atual = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.empresa_atual = None
        else:
            self.empresa_atual = get_empresa_do_usuario(
                request.user
            )

            if self.empresa_atual is None:
                raise PermissionDenied(
                    "Usuario sem empresa vinculada."
                )

        return super().dispatch(
            request,
            *args,
            **kwargs,
        )

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_superuser:
            empresa_id = (
                self.request.GET.get("empresa")
                or self.request.POST.get("empresa")
            )

            if empresa_id:
                return queryset.filter(
                    empresa_id=empresa_id
                )

            prefeitura_contagem = (
                Empresa.objects
                .filter(
                    nome__iexact="Prefeitura de Contagem"
                )
                .first()
            )

            if prefeitura_contagem:
                return queryset.filter(
                    empresa=prefeitura_contagem
                )

            return queryset.none()

        return queryset.filter(
            empresa=self.empresa_atual
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_superuser:
            empresa_id = (
                self.request.GET.get("empresa")
                or self.request.POST.get("empresa")
            )

            if empresa_id:
                empresa_selecionada = (
                    Empresa.objects
                    .filter(pk=empresa_id)
                    .first()
                )
            else:
                empresa_selecionada = (
                    Empresa.objects
                    .filter(
                        nome__iexact="Prefeitura de Contagem"
                    )
                    .first()
                )

            context["empresa_selecionada"] = (
                empresa_selecionada
            )
            context["empresas_disponiveis"] = (
                Empresa.objects.order_by("nome")
            )
        else:
            context["empresa_selecionada"] = (
                self.empresa_atual
            )
            context["empresas_disponiveis"] = (
                Empresa.objects.none()
            )

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.user.is_superuser:
            kwargs["permitir_empresa"] = True
        else:
            kwargs["empresa"] = self.empresa_atual

        return kwargs

    def form_valid(self, form):
        if self.request.user.is_superuser:
            empresa = form.cleaned_data.get("empresa")

            if not empresa:
                raise PermissionDenied(
                    "Informe a empresa."
                )
        else:
            empresa = self.empresa_atual

        form.instance.empresa = empresa

        return super().form_valid(form)


class CargoList(
    CadastroAuxiliarMixin,
    ListView,
):
    model = Cargo
    permission_required = (
        "funcionarios.view_cargo"
    )
    template_name = (
        "funcionarios/cadastros_auxiliares_list.html"
    )
    context_object_name = "objetos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "titulo": "Cargos",
            "singular": "Cargo",
            "tipo": "cargo",
            "url_novo": "create_cargo",
            "url_editar": "update_cargo",
            "url_excluir": "delete_cargo",
        })
        return context


class CargoCreate(
    CadastroAuxiliarMixin,
    CreateView,
):
    model = Cargo
    form_class = CargoForm
    permission_required = (
        "funcionarios.add_cargo"
    )
    template_name = (
        "funcionarios/cadastro_auxiliar_form.html"
    )
    success_url = reverse_lazy("list_cargos")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "titulo": "Novo cargo",
            "voltar_url": "list_cargos",
        })
        return context


class CargoUpdate(
    CadastroAuxiliarMixin,
    UpdateView,
):
    model = Cargo
    form_class = CargoForm
    permission_required = (
        "funcionarios.change_cargo"
    )
    template_name = (
        "funcionarios/cadastro_auxiliar_form.html"
    )
    success_url = reverse_lazy("list_cargos")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "titulo": "Editar cargo",
            "voltar_url": "list_cargos",
        })
        return context


class CargoDelete(
    CadastroAuxiliarMixin,
    DeleteView,
):
    model = Cargo
    permission_required = (
        "funcionarios.delete_cargo"
    )
    template_name = (
        "funcionarios/cadastro_auxiliar_confirm_delete.html"
    )
    success_url = reverse_lazy("list_cargos")


class NivelList(
    CadastroAuxiliarMixin,
    ListView,
):
    model = Nivel
    permission_required = (
        "funcionarios.view_nivel"
    )
    template_name = (
        "funcionarios/cadastros_auxiliares_list.html"
    )
    context_object_name = "objetos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "titulo": "N?veis",
            "singular": "N?vel",
            "tipo": "nivel",
            "url_novo": "create_nivel",
            "url_editar": "update_nivel",
            "url_excluir": "delete_nivel",
        })
        return context


class NivelCreate(
    CadastroAuxiliarMixin,
    CreateView,
):
    model = Nivel
    form_class = NivelForm
    permission_required = (
        "funcionarios.add_nivel"
    )
    template_name = (
        "funcionarios/cadastro_auxiliar_form.html"
    )
    success_url = reverse_lazy("list_niveis")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "titulo": "Novo n?vel",
            "voltar_url": "list_niveis",
        })
        return context


class NivelUpdate(
    CadastroAuxiliarMixin,
    UpdateView,
):
    model = Nivel
    form_class = NivelForm
    permission_required = (
        "funcionarios.change_nivel"
    )
    template_name = (
        "funcionarios/cadastro_auxiliar_form.html"
    )
    success_url = reverse_lazy("list_niveis")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "titulo": "Editar n?vel",
            "voltar_url": "list_niveis",
        })
        return context


class NivelDelete(
    CadastroAuxiliarMixin,
    DeleteView,
):
    model = Nivel
    permission_required = (
        "funcionarios.delete_nivel"
    )
    template_name = (
        "funcionarios/cadastro_auxiliar_confirm_delete.html"
    )
    success_url = reverse_lazy("list_niveis")


class EquipamentoList(
    CadastroAuxiliarMixin,
    ListView,
):
    model = Equipamento
    permission_required = (
        "funcionarios.view_equipamento"
    )
    template_name = (
        "funcionarios/cadastros_auxiliares_list.html"
    )
    context_object_name = "objetos"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "titulo": "Equipamentos",
            "singular": "Equipamento",
            "tipo": "equipamento",
            "url_novo": "create_equipamento",
            "url_editar": "update_equipamento",
            "url_excluir": "delete_equipamento",
        })
        return context


class EquipamentoCreate(
    CadastroAuxiliarMixin,
    CreateView,
):
    model = Equipamento
    form_class = EquipamentoForm
    permission_required = (
        "funcionarios.add_equipamento"
    )
    template_name = (
        "funcionarios/cadastro_auxiliar_form.html"
    )
    success_url = reverse_lazy(
        "list_equipamentos"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "titulo": "Novo equipamento",
            "voltar_url": "list_equipamentos",
        })
        return context


class EquipamentoUpdate(
    CadastroAuxiliarMixin,
    UpdateView,
):
    model = Equipamento
    form_class = EquipamentoForm
    permission_required = (
        "funcionarios.change_equipamento"
    )
    template_name = (
        "funcionarios/cadastro_auxiliar_form.html"
    )
    success_url = reverse_lazy(
        "list_equipamentos"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "titulo": "Editar equipamento",
            "voltar_url": "list_equipamentos",
        })
        return context


class EquipamentoDelete(
    CadastroAuxiliarMixin,
    DeleteView,
):
    model = Equipamento
    permission_required = (
        "funcionarios.delete_equipamento"
    )
    template_name = (
        "funcionarios/cadastro_auxiliar_confirm_delete.html"
    )
    success_url = reverse_lazy(
        "list_equipamentos"
    )
