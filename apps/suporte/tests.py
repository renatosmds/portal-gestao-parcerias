from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.suporte.models import ArtigoConhecimento, ChamadoSuporte


class SuporteTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="usuario", password="Teste@123")
        self.client.force_login(self.user)

    def test_painel_abre(self):
        self.assertEqual(self.client.get(reverse("suporte_painel")).status_code, 200)

    def test_abre_chamado(self):
        response = self.client.post(reverse("suporte_chamado_novo"), {
            "assunto": "Dúvida de teste", "categoria": "tecnico", "prioridade": "normal",
            "descricao": "Descrição da dúvida", "pagina_origem": "/",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ChamadoSuporte.objects.filter(solicitante=self.user).exists())

    def test_artigo_abre(self):
        artigo = ArtigoConhecimento.objects.create(titulo="Como acessar", slug="como-acessar", categoria="acesso", conteudo="Conteúdo", ativo=True)
        self.assertEqual(self.client.get(reverse("suporte_artigo", args=[artigo.slug])).status_code, 200)
