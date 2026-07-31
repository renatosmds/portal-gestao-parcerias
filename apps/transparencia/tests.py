from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.documentos.models import Documento
from apps.termos.models import Termos
from .models import PublicacaoDocumento, PublicacaoParceria


class TransparenciaTests(TestCase):
    def setUp(self):
        self.termo = Termos.objects.create(numtermo="001/2026", nomeosc="OSC Teste", objeto="Objeto público", valorglobal=1000, valorrepasse=800, status="Vigente")
        self.publicacao = PublicacaoParceria.objects.create(termo=self.termo, publicada=True)
        self.staff = get_user_model().objects.create_user("admin24", password="teste123", is_staff=True)

    def test_portal_abre_sem_login(self):
        response = self.client.get(reverse("transparencia_publica"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OSC Teste")

    def test_parceria_nao_publicada_nao_aparece(self):
        self.publicacao.publicada = False
        self.publicacao.save()
        response = self.client.get(reverse("transparencia_publica"))
        self.assertNotContains(response, "OSC Teste")

    def test_gestao_exige_usuario_staff(self):
        response = self.client.get(reverse("transparencia_painel"))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="admin24", password="teste123")
        response = self.client.get(reverse("transparencia_painel"))
        self.assertEqual(response.status_code, 200)

    def test_documento_restrito_nao_pode_ser_baixado(self):
        documento = Documento.objects.create(descricao="Documento restrito", arquivo="documentos/restrito.pdf", termo=self.termo)
        pub = PublicacaoDocumento.objects.create(documento=documento, classificacao=PublicacaoDocumento.Classificacao.RESTRITO, publicado=False)
        response = self.client.get(reverse("transparencia_documento_publico", args=[pub.pk]))
        self.assertEqual(response.status_code, 404)

    def test_json_publica_somente_parcerias_liberadas(self):
        response = self.client.get(reverse("transparencia_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["resultados"]), 1)
