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
from apps.pareceres.versionamento import (
    criar_nova_versao_parecer,
)
from apps.prestacao.models import Prestacao


User = get_user_model()


class Sprint4614VersionamentoParecerTests(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_superuser(
            username="versionador4614",
            email="versionador4614@example.com",
            password="teste123",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 46.14",
        )

        self.prestacao = Prestacao.objects.create(
            tipo="MENSAL",
            empresa=self.empresa,
        )

        self.parecer = ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            numero="PT-4614",
            versao=1,
            situacao=ParecerTecnico.Situacao.FINALIZADO,
            tipo_conclusao=(
                ParecerTecnico.TipoConclusao.COM_RESSALVAS
            ),
            resumo_executivo="Resumo da vers?o 1.",
            fundamentacao_geral="Fundamenta??o da vers?o 1.",
            conclusao="Conclus?o da vers?o 1.",
            ressalvas="Ressalvas da vers?o 1.",
            recomendacoes_gerais="Recomenda??es da vers?o 1.",
            elaborado_por=self.usuario,
            revisado_por=self.usuario,
            revisado_em=timezone.now(),
            aprovado_por=self.usuario,
            aprovado_em=timezone.now(),
        )

        self.item = ItemParecer.objects.create(
            parecer=self.parecer,
            codigo="VER-001",
            titulo="Item da vers?o original",
            descricao="Descri??o original",
            fato_verificado="Fato original",
            evidencia="Evid?ncia original",
            fundamentacao="Fundamenta??o original",
            recomendacao="Recomenda??o original",
            manifestacao_analista="Manifesta??o original",
            conclusao_item=(
                ItemParecer.ConclusaoItem.RESSALVA
            ),
            criado_por=self.usuario,
        )

        self.client.force_login(
            self.usuario
        )

    def _nova(self):
        return criar_nova_versao_parecer(
            parecer=self.parecer,
            usuario=self.usuario,
        )

    def test_nova_versao_incrementa_numero(self):
        nova = self._nova()

        self.assertEqual(
            nova.versao,
            2,
        )

    def test_nova_versao_referencia_anterior(self):
        nova = self._nova()

        self.assertEqual(
            nova.versao_anterior,
            self.parecer,
        )

    def test_versao_anterior_fica_substituida(self):
        self._nova()

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.situacao,
            ParecerTecnico.Situacao.SUBSTITUIDO,
        )

    def test_nova_versao_inicia_rascunho(self):
        nova = self._nova()

        self.assertEqual(
            nova.situacao,
            ParecerTecnico.Situacao.RASCUNHO,
        )

    def test_nova_versao_nao_herda_revisao_aprovacao(self):
        nova = self._nova()

        self.assertIsNone(
            nova.revisado_por
        )
        self.assertIsNone(
            nova.revisado_em
        )
        self.assertIsNone(
            nova.aprovado_por
        )
        self.assertIsNone(
            nova.aprovado_em
        )

    def test_nova_versao_preserva_conteudo_tecnico(self):
        nova = self._nova()

        self.assertEqual(
            nova.tipo_conclusao,
            self.parecer.tipo_conclusao,
        )
        self.assertEqual(
            nova.resumo_executivo,
            self.parecer.resumo_executivo,
        )
        self.assertEqual(
            nova.conclusao,
            self.parecer.conclusao,
        )

    def test_itens_sao_copiados(self):
        nova = self._nova()

        self.assertEqual(
            nova.itens.count(),
            1,
        )

        item_novo = nova.itens.get()

        self.assertNotEqual(
            item_novo.pk,
            self.item.pk,
        )

        self.assertEqual(
            item_novo.codigo,
            self.item.codigo,
        )

        self.assertEqual(
            item_novo.manifestacao_analista,
            self.item.manifestacao_analista,
        )

    def test_nao_cria_versao_de_parecer_nao_finalizado(self):
        self.parecer.situacao = (
            ParecerTecnico.Situacao.EM_REVISAO
        )
        self.parecer.save()

        with self.assertRaises(Exception):
            self._nova()

    def test_nao_permite_duas_sucessoras(self):
        self._nova()

        self.parecer.refresh_from_db()

        with self.assertRaises(Exception):
            criar_nova_versao_parecer(
                parecer=self.parecer,
                usuario=self.usuario,
            )

        self.assertEqual(
            ParecerTecnico.objects.filter(
                prestacao=self.prestacao,
            ).count(),
            2,
        )

    def test_versionamento_gera_auditoria_nas_duas_versoes(self):
        nova = self._nova()

        self.assertTrue(
            HistoricoParecer.objects.filter(
                parecer=self.parecer,
                acao="PARECER_SUBSTITUIDO",
            ).exists()
        )

        self.assertTrue(
            HistoricoParecer.objects.filter(
                parecer=nova,
                acao="NOVA_VERSAO_CRIADA",
            ).exists()
        )

    def test_get_nao_cria_nova_versao(self):
        resposta = self.client.get(
            reverse(
                "pareceres:parecer_nova_versao",
                args=[self.parecer.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            405,
        )

        self.assertEqual(
            ParecerTecnico.objects.count(),
            1,
        )

    def test_post_cria_e_redireciona_para_nova_versao(self):
        resposta = self.client.post(
            reverse(
                "pareceres:parecer_nova_versao",
                args=[self.parecer.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        nova = ParecerTecnico.objects.get(
            prestacao=self.prestacao,
            versao=2,
        )

        self.assertIn(
            str(nova.pk),
            resposta.url,
        )

    def test_interface_mostra_versionamento(self):
        resposta = self.client.get(
            reverse(
                "pareceres:parecer_detalhe",
                args=[self.parecer.pk],
            )
        )

        self.assertContains(
            resposta,
            "Versão:",
        )

        self.assertContains(
            resposta,
            "Criar nova versão",
        )
