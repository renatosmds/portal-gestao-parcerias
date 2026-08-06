from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.urls import reverse

from apps.prestacao.models import Prestacao

from .models import MetaExecucao


class MetasTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="teste",
            password="123",
            is_staff=True,
        )

        grupo, _ = Group.objects.get_or_create(
            name="Técnico de Execução"
        )

        permissao = Permission.objects.get(
            content_type__app_label="metas",
            codename="view_metaexecucao",
        )

        grupo.permissions.add(permissao)
        self.user.groups.add(grupo)

        self.prestacao = Prestacao.objects.create(
            tipo="cnpj",
            numtermo="TC 001/2026",
        )

    def test_painel_exige_login(self):
        response = self.client.get(reverse("metas_painel"))
        self.assertEqual(response.status_code, 302)

    def test_painel_abre_para_usuario_autenticado(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("metas_painel"))

        self.assertEqual(response.status_code, 200)

    def test_percentual_execucao(self):
        meta = MetaExecucao.objects.create(
            prestacao=self.prestacao,
            titulo="Atendimentos",
            valor_previsto=100,
            valor_realizado=75,
        )

        self.assertEqual(float(meta.percentual_execucao), 75.0)
