from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.empresas.models import Empresa
from apps.pareceres.models import (
    HistoricoParecer,
    ItemParecer,
    ParecerTecnico,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint4613AprovacaoParecerTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_superuser(
            username="aprovador4613",
            email="aprovador4613@example.com",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.13",
        )

        self.prestacao = Prestacao.objects.create(
            tipo="MENSAL",
            empresa=self.empresa,
        )

        self.parecer = ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            elaborado_por=self.usuario,
            tipo_conclusao=(
                ParecerTecnico.TipoConclusao.COM_RESSALVAS
            ),
        )

        self.item = ItemParecer.objects.create(
            parecer=self.parecer,
            codigo="APR-001",
            titulo="Item para aprova??o",
            fato_verificado="Fato revisado.",
            conclusao_item=(
                ItemParecer.ConclusaoItem.RESSALVA
            ),
            criado_por=self.usuario,
        )

        self.client.force_login(
            self.usuario
        )

    def _marcar_revisado(self):
        self.parecer.situacao = (
            ParecerTecnico.Situacao.EM_REVISAO
        )
        self.parecer.revisado_por = self.usuario
        self.parecer.revisado_em = timezone.now()

        self.parecer.save(
            update_fields=[
                "situacao",
                "revisado_por",
                "revisado_em",
                "atualizado_em",
            ]
        )

    def _aprovar(self):
        return self.client.post(
            reverse(
                "pareceres:parecer_aprovar",
                args=[self.parecer.pk],
            )
        )

    def test_get_aprovacao_nao_altera_parecer(self):
        self._marcar_revisado()

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_aprovar",
                args=[self.parecer.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            405,
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.situacao,
            ParecerTecnico.Situacao.EM_REVISAO,
        )

        self.assertIsNone(
            self.parecer.aprovado_por
        )

    def test_parecer_nao_revisado_nao_pode_ser_aprovado(self):
        resposta = self._aprovar()

        self.assertEqual(
            resposta.status_code,
            403,
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.situacao,
            ParecerTecnico.Situacao.RASCUNHO,
        )

    def test_parecer_revisado_pode_ser_aprovado(self):
        self._marcar_revisado()

        resposta = self._aprovar()

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.situacao,
            ParecerTecnico.Situacao.FINALIZADO,
        )

    def test_aprovacao_registra_usuario(self):
        self._marcar_revisado()

        self._aprovar()

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.aprovado_por,
            self.usuario,
        )

    def test_aprovacao_registra_data(self):
        self._marcar_revisado()

        self._aprovar()

        self.parecer.refresh_from_db()

        self.assertIsNotNone(
            self.parecer.aprovado_em
        )

    def test_aprovacao_gera_historico(self):
        self._marcar_revisado()

        self._aprovar()

        historico = HistoricoParecer.objects.get(
            parecer=self.parecer,
            acao="PARECER_APROVADO",
        )

        self.assertEqual(
            historico.usuario,
            self.usuario,
        )

        self.assertEqual(
            historico.situacao_anterior,
            ParecerTecnico.Situacao.EM_REVISAO,
        )

        self.assertEqual(
            historico.nova_situacao,
            ParecerTecnico.Situacao.FINALIZADO,
        )

    def test_aprovacao_preserva_tipo_conclusao(self):
        self._marcar_revisado()

        conclusao_antes = (
            self.parecer.tipo_conclusao
        )

        self._aprovar()

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.tipo_conclusao,
            conclusao_antes,
        )

    def test_parecer_nao_pode_ser_aprovado_duas_vezes(self):
        self._marcar_revisado()

        primeira = self._aprovar()
        segunda = self._aprovar()

        self.assertEqual(
            primeira.status_code,
            302,
        )

        self.assertEqual(
            segunda.status_code,
            403,
        )

        self.assertEqual(
            HistoricoParecer.objects.filter(
                parecer=self.parecer,
                acao="PARECER_APROVADO",
            ).count(),
            1,
        )

    def test_parecer_finalizado_fica_bloqueado_para_edicao(self):
        self._marcar_revisado()

        self._aprovar()

        resposta_parecer = self.client.get(
            reverse(
                "pareceres:parecer_revisar",
                args=[self.parecer.pk],
            )
        )

        resposta_item = self.client.get(
            reverse(
                "pareceres:item_revisar",
                args=[self.item.pk],
            )
        )

        self.assertEqual(
            resposta_parecer.status_code,
            403,
        )

        self.assertEqual(
            resposta_item.status_code,
            403,
        )

    def test_detalhe_exibe_aprovacao_e_oculta_edicao(self):
        self._marcar_revisado()

        self._aprovar()

        resposta = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer.pk],
            )
        )

        self.assertContains(
            resposta,
            "Aprovado por:",
        )

        self.assertContains(
            resposta,
            self.usuario.username,
        )

        self.assertNotContains(
            resposta,
            "Aprovar parecer",
        )

        self.assertNotContains(
            resposta,
            "Revisar item",
        )
