from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase

from apps.core.acesso import usuario_eh_osc
from apps.core.context_processors import access_context
from apps.core.dashboard import _normalizar_visao


class AreaPerfilHomologacaoTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.factory = RequestFactory()

        self.analista = User.objects.create_user(
            username="analista_area_teste",
            password="teste123",
            is_staff=False,
            is_superuser=False,
        )

        self.osc = User.objects.create_user(
            username="osc_area_teste",
            password="teste123",
            is_staff=False,
            is_superuser=False,
        )

        grupo_analista = Group.objects.create(
            name=(
                "Analista de "
                "Presta\u00e7\u00e3o de Contas"
            )
        )

        grupo_osc = Group.objects.create(
            name="Usu\u00e1rio da OSC"
        )

        self.analista.groups.add(
            grupo_analista
        )

        self.osc.groups.add(
            grupo_osc
        )

    def request_para(self, user):
        request = self.factory.get("/")
        request.user = user
        return request

    def test_analista_nao_eh_osc(self):
        self.assertFalse(
            usuario_eh_osc(
                self.analista
            )
        )

    def test_osc_eh_osc(self):
        self.assertTrue(
            usuario_eh_osc(
                self.osc
            )
        )

    def test_dashboard_analista_abre_visao_orgao(self):
        request = self.request_para(
            self.analista
        )

        self.assertEqual(
            _normalizar_visao(request),
            "orgao",
        )

    def test_dashboard_usuario_osc_abre_visao_osc(self):
        request = self.request_para(
            self.osc
        )

        self.assertEqual(
            _normalizar_visao(request),
            "osc",
        )

    def test_contexto_analista_area_orgao(self):
        request = self.request_para(
            self.analista
        )

        contexto = access_context(
            request
        )

        self.assertFalse(
            contexto["usuario_area_osc"]
        )

        self.assertEqual(
            contexto["area_portal"],
            "\u00c1rea do \u00d3rg\u00e3o P\u00fablico",
        )

    def test_contexto_osc_area_osc(self):
        request = self.request_para(
            self.osc
        )

        contexto = access_context(
            request
        )

        self.assertTrue(
            contexto["usuario_area_osc"]
        )

        self.assertEqual(
            contexto["area_portal"],
            "\u00c1rea da OSC",
        )
