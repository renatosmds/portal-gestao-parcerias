from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from apps.core.testes_documentos import cpf_teste
from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.prestacao.models import Prestacao
from .models import Conciliacao, Movimentacao
from .services import importar_extrato


class ConciliacaoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("admin25", "admin25@example.com", "senha123")
        self.empresa = Empresa.objects.create(nome="OSC Sprint 25")
        self.prestacao = Prestacao.objects.create(tipoTermo="TC", numtermo="025/2026", tipo="cnpj", empresa=self.empresa)
        self.conciliacao = Conciliacao.objects.create(prestacao=self.prestacao, saldo_inicial=Decimal("100.00"), saldo_final_informado=Decimal("130.00"), criado_por=self.user)

    def test_saldo_calculado(self):
        Movimentacao.objects.create(conciliacao=self.conciliacao, data="2026-07-01", descricao="Repasse", tipo="credito", valor=Decimal("50.00"))
        Movimentacao.objects.create(conciliacao=self.conciliacao, data="2026-07-02", descricao="Pagamento", tipo="debito", valor=Decimal("20.00"))
        self.assertEqual(self.conciliacao.saldo_final_calculado, Decimal("130.00"))

    def test_importacao_csv(self):
        arq = SimpleUploadedFile("extrato.csv", "data;descricao;credito;debito\n01/07/2026;Repasse;100,00;\n02/07/2026;Compra;;25,50\n".encode(), content_type="text/csv")
        imp = importar_extrato(self.conciliacao, arq, self.user)
        self.assertEqual(imp.total_importadas, 2)
        self.assertEqual(self.conciliacao.movimentacoes.count(), 2)

    def test_painel_exige_login(self):
        resposta = self.client.get(reverse("conciliacao_painel"))
        self.assertEqual(resposta.status_code, 302)

    def test_superusuario_acessa_painel(self):
        self.client.force_login(self.user)
        resposta = self.client.get(reverse("conciliacao_painel"))
        self.assertEqual(resposta.status_code, 200)

    def test_recalculo_fechada_apos_conciliacao(self):
        mov = Movimentacao.objects.create(conciliacao=self.conciliacao, data="2026-07-03", descricao="Ajuste", tipo="credito", valor=Decimal("30.00"), situacao=Movimentacao.Situacao.CONCILIADA)
        self.conciliacao.recalcular_situacao()
        self.assertEqual(self.conciliacao.situacao, Conciliacao.Situacao.FECHADA)


class ConciliacaoEscopoMultiempresaTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.empresa_a = Empresa.objects.create(
            nome="OSC A Conciliacao",
        )
        self.empresa_b = Empresa.objects.create(
            nome="OSC B Conciliacao",
        )

        self.prestacao_a = Prestacao.objects.create(
            tipoTermo="TC",
            numtermo="CONC-A",
            tipo="cnpj",
            empresa=self.empresa_a,
        )
        self.prestacao_b = Prestacao.objects.create(
            tipoTermo="TC",
            numtermo="CONC-B",
            tipo="cnpj",
            empresa=self.empresa_b,
        )

        self.criador = User.objects.create_superuser(
            username="admin_conc_fixture",
            email="admin-conc-fixture@example.test",
            password="teste12345",
        )

        self.conciliacao_a = Conciliacao.objects.create(
            prestacao=self.prestacao_a,
            saldo_inicial=Decimal("100.00"),
            saldo_final_informado=Decimal("100.00"),
            criado_por=self.criador,
        )

        self.conciliacao_b = Conciliacao.objects.create(
            prestacao=self.prestacao_b,
            saldo_inicial=Decimal("200.00"),
            saldo_final_informado=Decimal("200.00"),
            criado_por=self.criador,
        )

        permissoes = Permission.objects.filter(
            content_type__app_label="conciliacao",
        )

        self.usuario_a = User.objects.create_user(
            username="conc_usuario_a",
            password="teste12345",
        )
        self.usuario_a.user_permissions.add(*permissoes)

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Usuario Conciliacao A",
            usuario="conc_usuario_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="conc-a@example.test",
            Telefone="-",
            user=self.usuario_a,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
        )

        self.staff_a = User.objects.create_user(
            username="conc_staff_a",
            password="teste12345",
            is_staff=True,
        )
        self.staff_a.user_permissions.add(*permissoes)

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Staff Conciliacao A",
            usuario="conc_staff_a",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="conc-staff-a@example.test",
            Telefone="-",
            user=self.staff_a,
            empresa=self.empresa_a,
            imagem="funcionarios/teste.jpg",
        )

        self.usuario_b = User.objects.create_user(
            username="conc_usuario_b",
            password="teste12345",
        )
        self.usuario_b.user_permissions.add(*permissoes)

        Funcionario.objects.create(
            cpf=cpf_teste(),
            nome="Usuario Conciliacao B",
            usuario="conc_usuario_b",
            endereco="-",
            bairro="-",
            cep="-",
            cidade="Contagem",
            estado="MG",
            email="conc-b@example.test",
            Telefone="-",
            user=self.usuario_b,
            empresa=self.empresa_b,
            imagem="funcionarios/teste.jpg",
        )

        self.usuario_sem_empresa = User.objects.create_user(
            username="conc_sem_empresa",
            password="teste12345",
        )
        self.usuario_sem_empresa.user_permissions.add(
            *permissoes
        )

        self.gestor = User.objects.create_user(
            username="conc_gestor",
            password="teste12345",
        )
        self.gestor.user_permissions.add(*permissoes)

        grupo, _ = Group.objects.get_or_create(
            name="Gestor Municipal",
        )
        self.gestor.groups.add(grupo)

    def _ids_painel(self, usuario):
        self.client.force_login(usuario)

        response = self.client.get(
            reverse("conciliacao_painel")
        )

        self.assertEqual(response.status_code, 200)

        conciliacoes = response.context.get(
            "conciliacoes",
            [],
        )

        return {
            item.pk
            for item in conciliacoes
        }

    def test_usuario_empresa_a_ve_apenas_conciliacao_a(self):
        self.assertEqual(
            self._ids_painel(self.usuario_a),
            {self.conciliacao_a.pk},
        )

    def test_staff_comum_nao_ganha_visao_global(self):
        self.assertEqual(
            self._ids_painel(self.staff_a),
            {self.conciliacao_a.pk},
        )

    def test_empresa_b_nao_acessa_detalhe_da_empresa_a(self):
        self.client.force_login(self.usuario_b)

        response = self.client.get(
            reverse(
                "conciliacao_detalhe",
                kwargs={"pk": self.conciliacao_a.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_usuario_sem_empresa_nao_recebe_conciliacoes(self):
        self.assertEqual(
            self._ids_painel(self.usuario_sem_empresa),
            set(),
        )

    def test_gestor_municipal_recebe_visao_global(self):
        self.assertEqual(
            self._ids_painel(self.gestor),
            {
                self.conciliacao_a.pk,
                self.conciliacao_b.pk,
            },
        )
