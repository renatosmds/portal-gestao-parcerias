from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.empresas.models import Empresa
from apps.financeiro.models import MovimentacaoFinanceira
from apps.financeiro.views import MovimentacaoFinanceiraList
from apps.funcionarios.models import Funcionario
from apps.prestacao.models import (
    CompetenciaPrestacao,
    Prestacao,
)
from apps.termos.models import Termos


class FinanceiroAcessoTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.factory = RequestFactory()

        self.empresa_a = Empresa.objects.create(
            nome="OSC Financeiro A"
        )
        self.empresa_b = Empresa.objects.create(
            nome="OSC Financeiro B"
        )

        self.termo_a = Termos.objects.create(
            empresa=self.empresa_a,
            numtermo="FIN-A/2026",
            termo="Termo Financeiro A",
        )
        self.termo_b = Termos.objects.create(
            empresa=self.empresa_b,
            numtermo="FIN-B/2026",
            termo="Termo Financeiro B",
        )

        self.prestacao_a = Prestacao.objects.create(
            empresa=self.empresa_a,
            termo=self.termo_a,
            tipo="MENSAL",
            numtermo="FIN-A/2026",
        )
        self.prestacao_b = Prestacao.objects.create(
            empresa=self.empresa_b,
            termo=self.termo_b,
            tipo="MENSAL",
            numtermo="FIN-B/2026",
        )

        self.competencia_a = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao_a,
                ano=2026,
                mes=9,
                data_inicial=date(2026, 9, 1),
                data_final=date(2026, 9, 30),
            )
        )
        self.competencia_b = (
            CompetenciaPrestacao.objects.create(
                prestacao=self.prestacao_b,
                ano=2026,
                mes=9,
                data_inicial=date(2026, 9, 1),
                data_final=date(2026, 9, 30),
            )
        )

        self.usuario_osc = User.objects.create_user(
            username="financeiro_osc_a",
            password="teste123",
        )

        self.usuario_sem_permissao = (
            User.objects.create_user(
                username="financeiro_sem_permissao",
                password="teste123",
            )
        )

        self.usuario_gestor = User.objects.create_user(
            username="financeiro_gestor",
            password="teste123",
        )

        Funcionario.objects.create(
            nome="Usuario OSC A",
            usuario="financeiro_osc_a",
            endereco="Rua Teste",
            bairro="Centro",
            cep="32000-000",
            cidade="Contagem",
            estado="MG",
            email="osc_a@example.com",
            Telefone="31999999999",
            user=self.usuario_osc,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
        )

        permissoes = Permission.objects.filter(
            content_type__app_label="financeiro",
            codename__in=[
                "view_movimentacaofinanceira",
                "add_movimentacaofinanceira",
                "change_movimentacaofinanceira",
                "delete_movimentacaofinanceira",
            ],
        )

        self.usuario_osc.user_permissions.add(
            *permissoes
        )

        self.usuario_gestor.user_permissions.add(
            *permissoes
        )

        grupo_gestor, _ = Group.objects.get_or_create(
            name="Gestor Municipal"
        )

        self.usuario_gestor.groups.add(
            grupo_gestor
        )

        self.movimento_a = (
            MovimentacaoFinanceira.objects.create(
                empresa=self.empresa_a,
                termo=self.termo_a,
                prestacao=self.prestacao_a,
                competencia=self.competencia_a,
                data=date(2026, 9, 8),
                tipo=MovimentacaoFinanceira.Tipo.REPASSE,
                valor=Decimal("100.00"),
                descricao="Movimento OSC A",
                criado_por=self.usuario_osc,
            )
        )

        self.movimento_b = (
            MovimentacaoFinanceira.objects.create(
                empresa=self.empresa_b,
                termo=self.termo_b,
                prestacao=self.prestacao_b,
                competencia=self.competencia_b,
                data=date(2026, 9, 8),
                tipo=MovimentacaoFinanceira.Tipo.REPASSE,
                valor=Decimal("900.00"),
                descricao="Movimento OSC B",
                criado_por=self.usuario_gestor,
            )
        )

    def queryset_lista(self, usuario, **params):
        request = self.factory.get(
            reverse(
                "list_movimentacoes_financeiras"
            ),
            params,
        )
        request.user = usuario

        view = MovimentacaoFinanceiraList()
        view.setup(request)

        return view.get_queryset()

    def test_create_salva_movimentacao_uma_unica_vez(self):
        self.client.force_login(
            self.usuario_gestor
        )

        eventos = []

        def registrar_save(
            sender,
            instance,
            created,
            **kwargs,
        ):
            if (
                instance.descricao
                == "Teste create save unico"
            ):
                eventos.append(
                    created
                )

        post_save.connect(
            registrar_save,
            sender=MovimentacaoFinanceira,
            dispatch_uid="financeiro_create_save_unico",
        )

        try:
            resposta = self.client.post(
                reverse(
                    "create_movimentacao_financeira"
                ),
                {
                    "empresa": self.empresa_a.pk,
                    "termo": self.termo_a.pk,
                    "prestacao": self.prestacao_a.pk,
                    "competencia": self.competencia_a.pk,
                    "data": "2026-09-08",
                    "tipo": (
                        MovimentacaoFinanceira.Tipo.REPASSE
                    ),
                    "valor": "321.00",
                    "descricao": (
                        "Teste create save unico"
                    ),
                    "documento": "",
                    "observacao": "",
                },
            )
        finally:
            post_save.disconnect(
                registrar_save,
                sender=MovimentacaoFinanceira,
                dispatch_uid="financeiro_create_save_unico",
            )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            eventos,
            [True],
        )

        self.assertEqual(
            MovimentacaoFinanceira.objects.filter(
                descricao="Teste create save unico"
            ).count(),
            1,
        )

    def test_update_salva_movimentacao_uma_unica_vez(self):
        self.client.force_login(
            self.usuario_gestor
        )

        eventos = []

        def registrar_save(
            sender,
            instance,
            created,
            **kwargs,
        ):
            if instance.pk == self.movimento_a.pk:
                eventos.append(
                    created
                )

        post_save.connect(
            registrar_save,
            sender=MovimentacaoFinanceira,
            dispatch_uid="financeiro_update_save_unico",
        )

        try:
            resposta = self.client.post(
                reverse(
                    "update_movimentacao_financeira",
                    args=[self.movimento_a.pk],
                ),
                {
                    "termo": self.termo_a.pk,
                    "prestacao": self.prestacao_a.pk,
                    "competencia": self.competencia_a.pk,
                    "data": "2026-09-08",
                    "tipo": (
                        MovimentacaoFinanceira.Tipo.REPASSE
                    ),
                    "valor": "150.00",
                    "descricao": (
                        "Movimento OSC A atualizado"
                    ),
                    "documento": "",
                    "observacao": "",
                },
            )
        finally:
            post_save.disconnect(
                registrar_save,
                sender=MovimentacaoFinanceira,
                dispatch_uid="financeiro_update_save_unico",
            )

        self.assertEqual(
            resposta.status_code,
            302,
        )

        self.assertEqual(
            eventos,
            [False],
        )

        self.movimento_a.refresh_from_db()

        self.assertEqual(
            self.movimento_a.valor,
            Decimal("150.00"),
        )

    def test_osc_lista_apenas_propria_empresa(self):
        queryset = self.queryset_lista(
            self.usuario_osc
        )

        self.assertEqual(
            list(
                queryset.values_list(
                    "pk",
                    flat=True,
                )
            ),
            [self.movimento_a.pk],
        )

    def test_osc_nao_edita_movimento_outra_empresa(self):
        self.client.force_login(
            self.usuario_osc
        )

        resposta = self.client.get(
            reverse(
                "update_movimentacao_financeira",
                args=[self.movimento_b.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            404,
        )

    def test_osc_nao_exclui_movimento_outra_empresa(self):
        self.client.force_login(
            self.usuario_osc
        )

        resposta = self.client.post(
            reverse(
                "delete_movimentacao_financeira",
                args=[self.movimento_b.pk],
            )
        )

        self.assertEqual(
            resposta.status_code,
            404,
        )

        self.assertTrue(
            MovimentacaoFinanceira.objects.filter(
                pk=self.movimento_b.pk
            ).exists()
        )

    def test_ajax_termos_isola_empresa_osc(self):
        self.client.force_login(
            self.usuario_osc
        )

        resposta = self.client.get(
            reverse("financeiro_termos"),
            {
                "empresa": self.empresa_b.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        ids = {
            item["id"]
            for item in resposta.json()["termos"]
        }

        self.assertIn(
            self.termo_a.pk,
            ids,
        )
        self.assertNotIn(
            self.termo_b.pk,
            ids,
        )

    def test_ajax_prestacoes_nao_expoe_outra_osc(self):
        self.client.force_login(
            self.usuario_osc
        )

        resposta = self.client.get(
            reverse("financeiro_prestacoes"),
            {
                "termo": self.termo_b.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertEqual(
            resposta.json()["prestacoes"],
            [],
        )

    def test_ajax_competencias_nao_expoe_outra_osc(self):
        self.client.force_login(
            self.usuario_osc
        )

        resposta = self.client.get(
            reverse("financeiro_competencias"),
            {
                "prestacao": self.prestacao_b.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        self.assertEqual(
            resposta.json()["competencias"],
            [],
        )

    def test_usuario_sem_permissao_recebe_403_na_lista(self):
        self.client.force_login(
            self.usuario_sem_permissao
        )

        resposta = self.client.get(
            reverse(
                "list_movimentacoes_financeiras"
            )
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

    def test_usuario_sem_permissao_recebe_403_no_ajax(self):
        self.client.force_login(
            self.usuario_sem_permissao
        )

        resposta = self.client.get(
            reverse("financeiro_termos"),
            {
                "empresa": self.empresa_a.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            403,
        )

    def test_gestor_global_pode_filtrar_empresa(self):
        queryset = self.queryset_lista(
            self.usuario_gestor,
            empresa=str(self.empresa_b.pk),
        )

        self.assertEqual(
            list(
                queryset.values_list(
                    "pk",
                    flat=True,
                )
            ),
            [self.movimento_b.pk],
        )

    def test_gestor_global_consulta_termos_por_empresa(self):
        self.client.force_login(
            self.usuario_gestor
        )

        resposta = self.client.get(
            reverse("financeiro_termos"),
            {
                "empresa": self.empresa_b.pk,
            },
        )

        self.assertEqual(
            resposta.status_code,
            200,
        )

        ids = {
            item["id"]
            for item in resposta.json()["termos"]
        }

        self.assertIn(
            self.termo_b.pk,
            ids,
        )
        self.assertNotIn(
            self.termo_a.pk,
            ids,
        )
