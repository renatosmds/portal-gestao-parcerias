from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint4611RevisaoHumanaTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin4611",
            email="admin4611@example.com",
            password="teste123",
        )

        self.usuario_sem_escopo = User.objects.create_user(
            username="sem_escopo4611",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.11",
        )

        self.prestacao = Prestacao.objects.create(
            tipo="MENSAL",
            empresa=self.empresa,
        )

        self.parecer = ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            elaborado_por=self.admin,
        )

        self.item = ItemParecer.objects.create(
            parecer=self.parecer,
            codigo="REV-001",
            titulo="Item para revis?o humana",
            fato_verificado="Fato originalmente identificado.",
            conclusao_item=(
                ItemParecer.ConclusaoItem.NAO_ANALISADO
            ),
            criado_por=self.admin,
        )

    def test_lista_exige_login(self):
        resposta = self.client.get(
            reverse(
                "pareceres:parecer_lista"
            )
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

    def test_superusuario_acessa_lista_e_detalhe(self):
        self.client.force_login(
            self.admin
        )

        lista = self.client.get(
            reverse(
                "pareceres:parecer_lista"
            )
        )

        detalhe = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer.pk],
            )
        )

        self.assertEqual(
            lista.status_code,
            200,
        )

        self.assertEqual(
            detalhe.status_code,
            200,
        )

    def test_usuario_sem_escopo_nao_acessa_parecer(self):
        self.client.force_login(
            self.usuario_sem_escopo
        )

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            404,
        )

    def test_tela_separa_sugestao_de_decisao_humana(self):
        self.client.force_login(
            self.admin
        )

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_revisar",
                args=[self.parecer.pk],
            )
        )

        self.assertContains(
            resposta,
            "Sugestão automática",
        )

        self.assertContains(
            resposta,
            "Decisão e manifestação do analista",
        )

    def test_get_da_revisao_nao_altera_parecer(self):
        self.client.force_login(
            self.admin
        )

        conclusao_antes = (
            self.parecer.tipo_conclusao
        )

        self.client.get(
            reverse(
                "pareceres:parecer_revisar",
                args=[self.parecer.pk],
            )
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.tipo_conclusao,
            conclusao_antes,
        )

        self.assertIsNone(
            self.parecer.revisado_por
        )

    def test_post_registra_decisao_humana(self):
        self.client.force_login(
            self.admin
        )

        resposta = self.client.post(
            reverse(
                "pareceres:parecer_revisar",
                args=[self.parecer.pk],
            ),
            {
                "tipo_conclusao": (
                    ParecerTecnico.TipoConclusao.COM_RESSALVAS
                ),
                "resumo_executivo": (
                    "Resumo revisado pelo analista."
                ),
                "fundamentacao_geral": (
                    "Fundamenta??o revisada."
                ),
                "conclusao": (
                    "Conclus?o humana."
                ),
                "ressalvas": (
                    "Ressalva registrada."
                ),
                "recomendacoes_gerais": (
                    "Recomenda??o registrada."
                ),
            },
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.tipo_conclusao,
            ParecerTecnico.TipoConclusao.COM_RESSALVAS,
        )

        self.assertEqual(
            self.parecer.revisado_por,
            self.admin,
        )

        self.assertIsNotNone(
            self.parecer.revisado_em
        )

        self.assertEqual(
            self.parecer.situacao,
            ParecerTecnico.Situacao.EM_REVISAO,
        )

    def test_post_item_registra_manifestacao_humana(self):
        self.client.force_login(
            self.admin
        )

        resposta = self.client.post(
            reverse(
                "pareceres:item_revisar",
                args=[self.item.pk],
            ),
            {
                "fato_verificado": (
                    "Fato confirmado pelo analista."
                ),
                "evidencia": (
                    "Documento conferido."
                ),
                "fundamentacao": (
                    "Fundamenta??o conferida."
                ),
                "risco_glosa": (
                    "Risco sujeito a decis?o espec?fica."
                ),
                "recomendacao": (
                    "Registrar ressalva."
                ),
                "manifestacao_analista": (
                    "Ap?s confer?ncia, o item foi classificado "
                    "com ressalva."
                ),
                "conclusao_item": (
                    ItemParecer.ConclusaoItem.RESSALVA
                ),
            },
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.item.refresh_from_db()

        self.assertEqual(
            self.item.conclusao_item,
            ItemParecer.ConclusaoItem.RESSALVA,
        )

        self.assertIn(
            "Ap?s confer?ncia",
            self.item.manifestacao_analista,
        )
