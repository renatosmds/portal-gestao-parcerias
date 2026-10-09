from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.conciliacao.models import Conciliacao
from apps.diligencias.models import Diligencia
from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.pareceres.models import ParecerTecnico
from apps.parcerias.models import Parcerias
from apps.planos_trabalho.models import PlanoTrabalho
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


class FluxoFuncionalCompletoParceriaTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_superuser(
            username="admin_fluxo_completo",
            email="fluxo@example.test",
            password="teste12345",
        )

        self.empresa = Empresa.objects.create(
            nome="OSC Fluxo Completo",
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="FC-001/26",
            termo="Termo Fluxo Completo",
        )

        self.parceria = Parcerias.objects.create(
            nomeOSC="OSC Fluxo Completo",
            empresa=self.empresa,
            numtermo=self.termo,
        )

        self.plano = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano Fluxo Completo",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
        )

        self.prestacao = Prestacao.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            tipoTermo="TC",
            numtermo="FC-001/26",
            tipo="cnpj",
        )

        self.lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            numero_lancamento="FC-LANC-001",
            data_documento=date(2026, 5, 10),
            descricao="Despesa fluxo completo",
            valor_documento=Decimal("150.00"),
            criado_por=self.admin,
        )

        self.documento = Documento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            prestacao=self.prestacao,
            lancamento=self.lancamento,
            descricao="Documento fluxo completo",
            arquivo=SimpleUploadedFile(
                "fluxo.pdf",
                b"conteudo fluxo completo",
                content_type="application/pdf",
            ),
        )

        self.conciliacao = Conciliacao.objects.create(
            prestacao=self.prestacao,
            saldo_inicial=Decimal("100.00"),
            saldo_final_informado=Decimal("100.00"),
            criado_por=self.admin,
        )

        self.diligencia = Diligencia.objects.create(
            empresa=self.empresa,
            prestacao=self.prestacao,
            lancamento=self.lancamento,
            documento=self.documento,
            assunto="Diligencia fluxo completo",
            descricao="Pendencia do fluxo funcional",
            criada_por=self.admin,
        )

        self.parecer = ParecerTecnico.objects.create(
            empresa=self.empresa,
            prestacao=self.prestacao,
            numero="FC-PARECER-001",
            elaborado_por=self.admin,
        )

    def test_fluxo_completo_aparece_no_detalhe_da_parceria(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse(
                "detail_parceria",
                kwargs={"pk": self.parceria.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        fluxo = response.context[
            "fluxo_parceria"
        ]

        self.assertEqual(
            fluxo["termo"],
            self.termo,
        )

        self.assertEqual(
            list(fluxo["planos"]),
            [self.plano],
        )

        self.assertEqual(
            list(fluxo["prestacoes"]),
            [self.prestacao],
        )

        self.assertEqual(
            list(fluxo["lancamentos"]),
            [self.lancamento],
        )

        self.assertEqual(
            list(fluxo["documentos"]),
            [self.documento],
        )

        self.assertEqual(
            list(fluxo["conciliacoes"]),
            [self.conciliacao],
        )

        self.assertEqual(
            list(fluxo["diligencias"]),
            [self.diligencia],
        )

        self.assertEqual(
            list(fluxo["pareceres"]),
            [self.parecer],
        )

        self.assertEqual(
            fluxo["totais"],
            {
                "planos": 1,
                "prestacoes": 1,
                "lancamentos": 1,
                "documentos": 1,
                "conciliacoes": 1,
                "diligencias": 1,
                "pareceres": 1,
            },
        )

        self.assertContains(
            response,
            "Fluxo funcional da parceria",
        )
        self.assertContains(
            response,
            "Plano de Trabalho",
        )
        self.assertContains(
            response,
            "Presta??o de Contas",
        )
        self.assertContains(
            response,
            "Concilia??o banc?ria",
        )
        self.assertContains(
            response,
            "Parecer T?cnico",
        )

    def test_fluxo_nao_expoe_modulo_sem_permissao(self):
        User = get_user_model()

        usuario = User.objects.create_user(
            username="fluxo_so_parcerias",
            password="teste12345",
        )

        permissao = Permission.objects.get(
            content_type__app_label="parcerias",
            codename="view_parcerias",
        )
        usuario.user_permissions.add(
            permissao
        )

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal",
        )
        usuario.groups.add(grupo)

        self.client.force_login(usuario)

        response = self.client.get(
            reverse(
                "detail_parceria",
                kwargs={"pk": self.parceria.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        fluxo = response.context[
            "fluxo_parceria"
        ]

        self.assertIsNone(
            fluxo["termo"]
        )
        self.assertEqual(
            fluxo["planos"].count(),
            0,
        )
        self.assertEqual(
            fluxo["prestacoes"].count(),
            0,
        )
        self.assertEqual(
            fluxo["lancamentos"].count(),
            0,
        )
        self.assertEqual(
            fluxo["documentos"].count(),
            0,
        )
        self.assertEqual(
            fluxo["conciliacoes"].count(),
            0,
        )
        self.assertEqual(
            fluxo["diligencias"].count(),
            0,
        )
        self.assertEqual(
            fluxo["pareceres"].count(),
            0,
        )

    def test_objetos_do_fluxo_pertencem_ao_mesmo_termo_e_empresa(self):
        self.assertEqual(
            self.parceria.numtermo,
            self.termo,
        )
        self.assertEqual(
            self.plano.termo,
            self.termo,
        )
        self.assertEqual(
            self.prestacao.termo,
            self.termo,
        )
        self.assertEqual(
            self.lancamento.termo,
            self.termo,
        )
        self.assertEqual(
            self.documento.termo,
            self.termo,
        )

        self.assertEqual(
            self.parceria.empresa,
            self.empresa,
        )
        self.assertEqual(
            self.prestacao.empresa,
            self.empresa,
        )
        self.assertEqual(
            self.lancamento.empresa,
            self.empresa,
        )
        self.assertEqual(
            self.documento.empresa,
            self.empresa,
        )
        self.assertEqual(
            self.diligencia.empresa,
            self.empresa,
        )
        self.assertEqual(
            self.parecer.empresa,
            self.empresa,
        )
