from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.empresas.models import Empresa
from apps.pareceres.models import (
    ItemParecer,
    ParecerTecnico,
)
from apps.prestacao.models import Prestacao


class ParecerExigeItensTests(TestCase):

    def setUp(self):

        User = get_user_model()

        self.usuario = User.objects.create_superuser(
            username="homologador_parecer_itens",
            email="homologador_itens@example.test",
            password="teste12345",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Homologação Parecer Itens",
        )

        self.prestacao = Prestacao.objects.create(
            tipo="MENSAL",
            empresa=self.empresa,
            numtermo="HOM-ITENS/2026",
        )

        self.parecer = ParecerTecnico.objects.create(
            prestacao=self.prestacao,
            empresa=self.empresa,
            numero="PT-HOM-ITENS",
            elaborado_por=self.usuario,
            situacao=ParecerTecnico.Situacao.EM_REVISAO,
            revisado_por=self.usuario,
            revisado_em=timezone.now(),
        )

        self.client.force_login(
            self.usuario
        )

    def test_parecer_sem_itens_nao_pode_ser_aprovado(self):

        response = self.client.post(
            reverse(
                "pareceres:parecer_aprovar",
                args=[self.parecer.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.situacao,
            ParecerTecnico.Situacao.EM_REVISAO,
        )

        self.assertIsNone(
            self.parecer.aprovado_por
        )

        self.assertIsNone(
            self.parecer.aprovado_em
        )

    def test_parecer_com_item_pode_ser_aprovado(self):

        ItemParecer.objects.create(
            parecer=self.parecer,
            codigo="HOM-001",
            titulo="Item de homologação",
            descricao=(
                "Item criado para validar a exigência "
                "mínima do parecer."
            ),
            origem=ItemParecer.Origem.MANUAL,
            conclusao_item=(
                ItemParecer.ConclusaoItem.REGULAR
            ),
            criado_por=self.usuario,
        )

        response = self.client.post(
            reverse(
                "pareceres:parecer_aprovar",
                args=[self.parecer.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.parecer.refresh_from_db()

        self.assertEqual(
            self.parecer.situacao,
            ParecerTecnico.Situacao.FINALIZADO,
        )

        self.assertEqual(
            self.parecer.aprovado_por,
            self.usuario,
        )

        self.assertIsNotNone(
            self.parecer.aprovado_em
        )
