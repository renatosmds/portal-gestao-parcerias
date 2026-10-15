from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.suporte.models import ArtigoConhecimento, ChamadoSuporte


class SuporteTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

        self.user = self.User.objects.create_user(
            username="usuario",
            password="Teste@123",
        )

        self.outro = self.User.objects.create_user(
            username="outro",
            password="Teste@123",
        )

        self.client.force_login(
            self.user
        )

    def test_painel_abre(self):
        self.assertEqual(
            self.client.get(
                reverse("suporte_painel")
            ).status_code,
            200,
        )

    def test_abre_chamado(self):
        response = self.client.post(
            reverse("suporte_chamado_novo"),
            {
                "assunto": "Duvida de teste",
                "categoria": "tecnico",
                "prioridade": "normal",
                "descricao": "Descricao da duvida",
                "pagina_origem": "/",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            ChamadoSuporte.objects.filter(
                solicitante=self.user
            ).exists()
        )

    def test_artigo_abre(self):
        artigo = ArtigoConhecimento.objects.create(
            titulo="Como acessar",
            slug="como-acessar",
            categoria="acesso",
            conteudo="Conteudo",
            ativo=True,
        )

        self.assertEqual(
            self.client.get(
                reverse(
                    "suporte_artigo",
                    args=[artigo.slug],
                )
            ).status_code,
            200,
        )

    def test_staff_sem_permissao_nao_ve_chamado_alheio(self):
        chamado = ChamadoSuporte.objects.create(
            solicitante=self.outro,
            assunto="Chamado privado",
            descricao="Teste",
            categoria="tecnico",
        )

        staff = self.User.objects.create_user(
            username="staff_sem_permissao",
            password="Teste@123",
            is_staff=True,
        )

        self.client.force_login(
            staff
        )

        response = self.client.get(
            reverse(
                "suporte_chamado_detalhe",
                args=[chamado.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_view_chamadosuporte_concede_visao_global(self):
        chamado = ChamadoSuporte.objects.create(
            solicitante=self.outro,
            assunto="Chamado auditoria",
            descricao="Teste",
            categoria="tecnico",
        )

        auditor = self.User.objects.create_user(
            username="auditor_suporte",
            password="Teste@123",
        )

        permissao = Permission.objects.get(
            content_type__app_label="suporte",
            codename="view_chamadosuporte",
        )

        auditor.user_permissions.add(
            permissao
        )

        self.client.force_login(
            auditor
        )

        response = self.client.get(
            reverse(
                "suporte_chamado_detalhe",
                args=[chamado.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
