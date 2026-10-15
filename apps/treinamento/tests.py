from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from apps.treinamento.models import ProgressoTreinamento
from apps.treinamento.views import _perfil


class TreinamentoTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

        self.user = self.User.objects.create_user(
            username="aluno",
            password="Teste@123",
        )

        self.client.force_login(
            self.user
        )

    def test_painel_abre(self):
        response = self.client.get(
            reverse("treinamento_painel")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_modulo_abre(self):
        response = self.client.get(
            reverse(
                "treinamento_modulo",
                args=["primeiros-passos"],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_concluir_modulo(self):
        response = self.client.post(
            reverse(
                "treinamento_concluir",
                args=["primeiros-passos"],
            ),
            {
                "concluido": "1"
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        progresso = ProgressoTreinamento.objects.get(
            usuario=self.user,
            modulo="primeiros-passos",
        )

        self.assertTrue(
            progresso.concluido
        )

    def test_staff_isolado_nao_e_administrador(self):
        staff = self.User.objects.create_user(
            username="staff_treinamento",
            password="Teste@123",
            is_staff=True,
        )

        self.assertEqual(
            _perfil(staff),
            "orgao",
        )

    def test_grupo_administrador_e_reconhecido(self):
        grupo, _ = Group.objects.get_or_create(
            name="Administrador do Sistema"
        )

        administrador = self.User.objects.create_user(
            username="administrador_treinamento",
            password="Teste@123",
        )

        administrador.groups.add(
            grupo
        )

        self.assertEqual(
            _perfil(administrador),
            "administrador",
        )

    def test_grupo_osc_e_reconhecido(self):
        grupo, _ = Group.objects.get_or_create(
            name="Usu\u00e1rio da OSC"
        )

        usuario_osc = self.User.objects.create_user(
            username="osc_treinamento",
            password="Teste@123",
        )

        usuario_osc.groups.add(
            grupo
        )

        self.assertEqual(
            _perfil(usuario_osc),
            "osc",
        )
