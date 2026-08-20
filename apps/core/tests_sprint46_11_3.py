from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.pareceres.forms import (
    ItemParecerRevisaoForm,
    ParecerRevisaoForm,
)
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint46113InterfaceFinalTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_superuser(
            username="admin46113",
            email="admin46113@example.com",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.11.3",
        )

        self.prestacao = Prestacao.objects.create(
            tipo="MENSAL",
            empresa=self.empresa,
        )

        self.parecer = ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            elaborado_por=self.usuario,
        )

        self.item = ItemParecer.objects.create(
            parecer=self.parecer,
            codigo="UI-001",
            titulo="Item de interface",
            criado_por=self.usuario,
        )

    def test_menu_exibe_pareceres_tecnicos(self):
        self.client.force_login(
            self.usuario
        )

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_lista"
            )
        )

        self.assertContains(
            resposta,
            "Pareceres Técnicos",
        )

    def test_form_parecer_possui_classes_bootstrap(self):
        form = ParecerRevisaoForm(
            instance=self.parecer
        )

        for field in form.fields.values():
            self.assertIn(
                "form-control",
                field.widget.attrs.get(
                    "class",
                    "",
                ),
            )

    def test_form_item_possui_classes_bootstrap(self):
        form = ItemParecerRevisaoForm(
            instance=self.item
        )

        for field in form.fields.values():
            self.assertIn(
                "form-control",
                field.widget.attrs.get(
                    "class",
                    "",
                ),
            )

    def test_menu_fica_ativo_no_namespace_pareceres(self):
        self.client.force_login(
            self.usuario
        )

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_lista"
            )
        )

        self.assertEqual(
            resposta.resolver_match.namespace,
            "pareceres",
        )
