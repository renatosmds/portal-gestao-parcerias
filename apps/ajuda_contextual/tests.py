from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import AjudaContextual

class AjudaContextualTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username="teste_ajuda",password="123",is_staff=True)
        self.ajuda=AjudaContextual.objects.create(modulo="termos",campo="objeto_teste",chave="termos-objeto-teste",titulo="Objeto",what="Descrição")
    def test_detalhe_exige_autenticacao_quando_interno(self):
        self.assertEqual(self.client.get(reverse("ajuda_contextual:detalhe",args=[self.ajuda.chave])).status_code,404)
    def test_detalhe_retorna_5w2h(self):
        self.client.force_login(self.user); r=self.client.get(reverse("ajuda_contextual:detalhe",args=[self.ajuda.chave])); self.assertEqual(r.status_code,200); self.assertEqual(r.json()["what"],"Descrição")
    def test_resolver_por_modulo_e_campo(self):
        self.client.force_login(self.user); r=self.client.get(reverse("ajuda_contextual:resolver"),{"campo":"objeto_teste","path":"/termos/novo/"}); self.assertTrue(r.json()["disponivel"]); self.assertEqual(r.json()["chave"],self.ajuda.chave)
    def test_gestao_exige_staff(self):
        comum=get_user_model().objects.create_user(username="comum",password="123"); self.client.force_login(comum); self.assertEqual(self.client.get(reverse("ajuda_contextual:gestao")).status_code,302)
