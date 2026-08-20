from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.pareceres.auditoria import registrar_historico
from apps.pareceres.models import (
    ParecerTecnico,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint46123AuditoriaInterfaceTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_superuser(
            username="auditor46123",
            email="auditor46123@example.com",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.12.3",
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

    def test_detalhe_exibe_secao_trilha_auditoria(self):
        self.client.force_login(
            self.usuario
        )

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer.pk],
            )
        )

        self.assertContains(
            resposta,
            "Trilha de auditoria",
        )

    def test_detalhe_exibe_evento_registrado(self):
        registrar_historico(
            parecer=self.parecer,
            acao="TESTE_AUDITORIA",
            usuario=self.usuario,
            situacao_anterior="RASCUNHO",
            nova_situacao="EM_REVISAO",
            observacao="Evento vis?vel na interface.",
        )

        self.client.force_login(
            self.usuario
        )

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer.pk],
            )
        )

        self.assertContains(
            resposta,
            "TESTE_AUDITORIA",
        )

        self.assertContains(
            resposta,
            "Evento vis?vel na interface.",
        )

        self.assertContains(
            resposta,
            "RASCUNHO",
        )

        self.assertContains(
            resposta,
            "EM_REVISAO",
        )

    def test_evento_exibe_usuario(self):
        registrar_historico(
            parecer=self.parecer,
            acao="AUTORIA_TESTE",
            usuario=self.usuario,
        )

        self.client.force_login(
            self.usuario
        )

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer.pk],
            )
        )

        self.assertContains(
            resposta,
            self.usuario.username,
        )

    def test_historico_mais_recente_aparece_primeiro(self):
        primeiro = registrar_historico(
            parecer=self.parecer,
            acao="PRIMEIRO_EVENTO",
            usuario=self.usuario,
        )

        segundo = registrar_historico(
            parecer=self.parecer,
            acao="SEGUNDO_EVENTO",
            usuario=self.usuario,
        )

        self.client.force_login(
            self.usuario
        )

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer.pk],
            )
        )

        conteudo = resposta.content.decode()

        self.assertLess(
            conteudo.index("SEGUNDO_EVENTO"),
            conteudo.index("PRIMEIRO_EVENTO"),
        )

        self.assertGreater(
            segundo.id,
            primeiro.id,
        )
