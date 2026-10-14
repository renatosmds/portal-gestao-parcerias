from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from apps.empresas.models import Empresa
from apps.importacoes.models import Importacao
from apps.lancamentos.models import Lancamento
from apps.importacoes.services import confirmar_importacao, validar_linhas
from apps.prestacao.models import CompetenciaPrestacao, Prestacao
from apps.termos.models import Termos

class ImportacoesTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "admin",
            password="x",
            is_staff=True,
        )

        permissao = Permission.objects.get(
            content_type__app_label="importacoes",
            codename="view_importacao",
        )

        self.user.user_permissions.add(
            permissao
        )

        self.client.force_login(
            self.user
        )
    def test_lista_abre(self):
        self.assertEqual(self.client.get(reverse("list_importacoes")).status_code, 200)
    def test_staff_sem_add_importacao_nao_abre_nova(self):
        response = self.client.get(
            reverse("create_importacao")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_usuario_com_view_e_add_importacao_abre_nova(self):
        permissao_add = Permission.objects.get(
            content_type__app_label="importacoes",
            codename="add_importacao",
        )

        self.user.user_permissions.add(
            permissao_add
        )

        response = self.client.get(
            reverse("create_importacao")
        )

        self.assertEqual(
            response.status_code,
            200,
        )
    def test_modelo(self):
        obj = Importacao.objects.create(tipo="osc", arquivo_nome="teste.csv", criado_por=self.user)
        self.assertEqual(obj.situacao, "validacao")


class ImportacoesPermissaoModuloTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.usuario = User.objects.create_user(
            username="usuario_sem_importacoes",
            password="teste12345",
        )

    def test_usuario_sem_modulo_nao_acessa_lista_por_url(self):
        self.client.force_login(
            self.usuario
        )

        response = self.client.get(
            reverse("list_importacoes")
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_usuario_com_view_importacao_acessa_lista(self):
        permissao = Permission.objects.get(
            content_type__app_label="importacoes",
            codename="view_importacao",
        )

        self.usuario.user_permissions.add(
            permissao
        )

        self.client.force_login(
            self.usuario
        )

        response = self.client.get(
            reverse("list_importacoes")
        )

        self.assertEqual(
            response.status_code,
            200,
        )



class ImportacaoTermosTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="importador_termos",
            password="teste12345",
        )

        self.empresa_a = Empresa.objects.create(
            nome="OSC Termos A"
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC Termos B"
        )

    def criar_importacao(
        self,
        empresa,
        objeto="Objeto inicial",
    ):
        return Importacao.objects.create(
            tipo="termo",
            arquivo_nome="termos.csv",
            criado_por=self.user,
            total_lido=1,
            linhas=[
                {
                    "numtermo": "HOM-001/26",
                    "empresa": empresa.nome,
                    "tipo": "Termo de Colabora??o",
                    "objeto": objeto,
                    "valor_global": "1000,00",
                    "valor_repasse": "900,00",
                }
            ],
        )

    def test_validacao_termo_exige_empresa(self):
        erros = validar_linhas(
            "termo",
            [
                {
                    "numtermo": "HOM-001/26",
                }
            ],
        )

        self.assertEqual(
            len(erros),
            1,
        )

        self.assertIn(
            "Empresa/OSC",
            erros[0]["erro"],
        )

    def test_importacao_termo_vincula_empresa(self):
        importacao = self.criar_importacao(
            self.empresa_a
        )

        confirmar_importacao(
            importacao
        )

        termo = Termos.objects.get(
            empresa=self.empresa_a,
            numtermo="HOM-001/26",
        )

        self.assertEqual(
            termo.empresa,
            self.empresa_a,
        )

        importacao.refresh_from_db()

        self.assertEqual(
            importacao.total_novos,
            1,
        )

        self.assertEqual(
            importacao.total_erros,
            0,
        )

    def test_mesmo_numero_em_empresas_diferentes(self):
        confirmar_importacao(
            self.criar_importacao(
                self.empresa_a
            )
        )

        confirmar_importacao(
            self.criar_importacao(
                self.empresa_b
            )
        )

        self.assertEqual(
            Termos.objects.filter(
                numtermo="HOM-001/26"
            ).count(),
            2,
        )

    def test_reimportacao_mesma_empresa_atualiza(self):
        confirmar_importacao(
            self.criar_importacao(
                self.empresa_a,
                objeto="Objeto original",
            )
        )

        segunda = self.criar_importacao(
            self.empresa_a,
            objeto="Objeto atualizado",
        )

        confirmar_importacao(
            segunda
        )

        self.assertEqual(
            Termos.objects.filter(
                empresa=self.empresa_a,
                numtermo="HOM-001/26",
            ).count(),
            1,
        )

        termo = Termos.objects.get(
            empresa=self.empresa_a,
            numtermo="HOM-001/26",
        )

        self.assertEqual(
            termo.objeto,
            "Objeto atualizado",
        )

        segunda.refresh_from_db()

        self.assertEqual(
            segunda.total_novos,
            0,
        )

        self.assertEqual(
            segunda.total_atualizados,
            1,
        )

    def test_empresa_inexistente_nao_cria_termo(self):
        importacao = Importacao.objects.create(
            tipo="termo",
            arquivo_nome="termos_invalido.csv",
            criado_por=self.user,
            total_lido=1,
            linhas=[
                {
                    "numtermo": "HOM-002/26",
                    "empresa": "OSC QUE NAO EXISTE",
                }
            ],
        )

        confirmar_importacao(
            importacao
        )

        importacao.refresh_from_db()

        self.assertEqual(
            importacao.situacao,
            "parcial",
        )

        self.assertEqual(
            importacao.total_erros,
            1,
        )

        self.assertFalse(
            Termos.objects.filter(
                numtermo="HOM-002/26"
            ).exists()
        )



class ImportacaoPrestacoesTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="importador_prestacoes",
            password="teste12345",
        )

        self.empresa_a = Empresa.objects.create(
            nome="OSC Prestacao A"
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC Prestacao B"
        )

        self.termo_a = Termos.objects.create(
            empresa=self.empresa_a,
            numtermo="HOM-PREST-01",
            termo="Termo Prestacao A",
        )

        self.termo_b = Termos.objects.create(
            empresa=self.empresa_b,
            numtermo="HOM-PREST-01",
            termo="Termo Prestacao B",
        )

    def criar_importacao(
        self,
        empresa,
        valor="1000,00",
    ):
        return Importacao.objects.create(
            tipo="prestacao",
            arquivo_nome="prestacoes.csv",
            criado_por=self.user,
            total_lido=1,
            linhas=[
                {
                    "numtermo": "HOM-PREST-01",
                    "empresa": empresa.nome,
                    "tipo_termo": "TC",
                    "tipo_pessoa": "cnpj",
                    "credor": empresa.nome,
                    "valor_contrato": valor,
                    "situacao_workflow": "elaboracao",
                }
            ],
        )

    def test_validacao_prestacao_exige_empresa(self):
        erros = validar_linhas(
            "prestacao",
            [
                {
                    "numtermo": "HOM-PREST-01",
                    "tipo_pessoa": "cnpj",
                }
            ],
        )

        self.assertEqual(
            len(erros),
            1,
        )

        self.assertIn(
            "Empresa/OSC",
            erros[0]["erro"],
        )

    def test_validacao_prestacao_exige_tipo_pessoa(self):
        erros = validar_linhas(
            "prestacao",
            [
                {
                    "numtermo": "HOM-PREST-01",
                    "empresa": self.empresa_a.nome,
                }
            ],
        )

        self.assertEqual(
            len(erros),
            1,
        )

        self.assertIn(
            "cpf ou cnpj",
            erros[0]["erro"],
        )

    def test_importacao_vincula_empresa_e_termo(self):
        importacao = self.criar_importacao(
            self.empresa_a
        )

        confirmar_importacao(
            importacao
        )

        prestacao = Prestacao.objects.get(
            empresa=self.empresa_a,
            numtermo="HOM-PREST-01",
        )

        self.assertEqual(
            prestacao.termo,
            self.termo_a,
        )

        self.assertEqual(
            prestacao.tipoTermo,
            "TC",
        )

        self.assertEqual(
            prestacao.tipo,
            "cnpj",
        )

        importacao.refresh_from_db()

        self.assertEqual(
            importacao.total_novos,
            1,
        )

        self.assertEqual(
            importacao.total_erros,
            0,
        )

    def test_mesmo_numero_em_empresas_diferentes(self):
        confirmar_importacao(
            self.criar_importacao(
                self.empresa_a
            )
        )

        confirmar_importacao(
            self.criar_importacao(
                self.empresa_b
            )
        )

        self.assertEqual(
            Prestacao.objects.filter(
                numtermo="HOM-PREST-01"
            ).count(),
            2,
        )

    def test_reimportacao_mesma_empresa_atualiza(self):
        confirmar_importacao(
            self.criar_importacao(
                self.empresa_a,
                valor="1000,00",
            )
        )

        segunda = self.criar_importacao(
            self.empresa_a,
            valor="1500,00",
        )

        confirmar_importacao(
            segunda
        )

        self.assertEqual(
            Prestacao.objects.filter(
                empresa=self.empresa_a,
                numtermo="HOM-PREST-01",
            ).count(),
            1,
        )

        prestacao = Prestacao.objects.get(
            empresa=self.empresa_a,
            numtermo="HOM-PREST-01",
        )

        self.assertEqual(
            prestacao.valorContrato,
            1500.0,
        )

        segunda.refresh_from_db()

        self.assertEqual(
            segunda.total_novos,
            0,
        )

        self.assertEqual(
            segunda.total_atualizados,
            1,
        )

    def test_termo_inexistente_nao_cria_prestacao(self):
        importacao = Importacao.objects.create(
            tipo="prestacao",
            arquivo_nome="prestacao_sem_termo.csv",
            criado_por=self.user,
            total_lido=1,
            linhas=[
                {
                    "numtermo": "TERMO-INEXISTENTE",
                    "empresa": self.empresa_a.nome,
                    "tipo_termo": "TC",
                    "tipo_pessoa": "cnpj",
                }
            ],
        )

        confirmar_importacao(
            importacao
        )

        importacao.refresh_from_db()

        self.assertEqual(
            importacao.situacao,
            "parcial",
        )

        self.assertEqual(
            importacao.total_erros,
            1,
        )

        self.assertFalse(
            Prestacao.objects.filter(
                empresa=self.empresa_a,
                numtermo="TERMO-INEXISTENTE",
            ).exists()
        )



class ImportacaoLancamentosTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="importador_lancamentos",
            password="teste12345",
        )

        self.empresa_a = Empresa.objects.create(
            nome="OSC Lancamento A"
        )

        self.empresa_b = Empresa.objects.create(
            nome="OSC Lancamento B"
        )

        self.termo_a = Termos.objects.create(
            empresa=self.empresa_a,
            numtermo="HOM-LANC-TC",
            termo="Termo Lancamento A",
        )

        self.termo_b = Termos.objects.create(
            empresa=self.empresa_b,
            numtermo="HOM-LANC-TC",
            termo="Termo Lancamento B",
        )

        self.prestacao_a = Prestacao.objects.create(
            empresa=self.empresa_a,
            termo=self.termo_a,
            tipo="cnpj",
            numtermo="HOM-LANC-PC",
        )

        self.prestacao_b = Prestacao.objects.create(
            empresa=self.empresa_b,
            termo=self.termo_b,
            tipo="cnpj",
            numtermo="HOM-LANC-PC",
        )

        self.competencia_a = CompetenciaPrestacao.objects.create(
            prestacao=self.prestacao_a,
            ano=2026,
            mes=1,
            data_inicial="2026-01-01",
            data_final="2026-01-31",
        )

        self.competencia_b = CompetenciaPrestacao.objects.create(
            prestacao=self.prestacao_b,
            ano=2026,
            mes=1,
            data_inicial="2026-01-01",
            data_final="2026-01-31",
        )

    def criar_importacao(
        self,
        empresa,
        descricao="Lancamento original",
        valor="100,00",
    ):
        return Importacao.objects.create(
            tipo="lancamento",
            arquivo_nome="lancamentos.csv",
            criado_por=self.user,
            total_lido=1,
            linhas=[
                {
                    "empresa": empresa.nome,
                    "numtermo": "HOM-LANC-TC",
                    "prestacao_numero": "HOM-LANC-PC",
                    "competencia_ano": "2026",
                    "competencia_mes": "1",
                    "numero_lancamento": "HOM-LANC-001",
                    "tipo_documento": "outro",
                    "numero_documento": "DOC-001",
                    "data_documento": "15/01/2026",
                    "descricao": descricao,
                    "valor_documento": valor,
                }
            ],
        )

    def test_validacao_exige_hierarquia(self):
        erros = validar_linhas(
            "lancamento",
            [
                {
                    "empresa": self.empresa_a.nome,
                    "numero_lancamento": "HOM-LANC-001",
                    "data_documento": "15/01/2026",
                    "descricao": "Teste",
                    "valor_documento": "100,00",
                }
            ],
        )

        self.assertEqual(
            len(erros),
            1,
        )

        self.assertIn(
            "Termo",
            erros[0]["erro"],
        )

    def test_importacao_vincula_hierarquia_completa(self):
        importacao = self.criar_importacao(
            self.empresa_a
        )

        confirmar_importacao(
            importacao
        )

        lancamento = Lancamento.objects.get(
            empresa=self.empresa_a,
            numero_lancamento="HOM-LANC-001",
        )

        self.assertEqual(
            lancamento.termo,
            self.termo_a,
        )

        self.assertEqual(
            lancamento.prestacao,
            self.prestacao_a,
        )

        self.assertEqual(
            lancamento.competencia,
            self.competencia_a,
        )

        importacao.refresh_from_db()

        self.assertEqual(
            importacao.total_novos,
            1,
        )

        self.assertEqual(
            importacao.total_erros,
            0,
        )

    def test_mesmo_numero_pode_existir_em_empresas_diferentes(self):
        confirmar_importacao(
            self.criar_importacao(
                self.empresa_a
            )
        )

        confirmar_importacao(
            self.criar_importacao(
                self.empresa_b
            )
        )

        self.assertEqual(
            Lancamento.objects.filter(
                numero_lancamento="HOM-LANC-001"
            ).count(),
            2,
        )

    def test_reimportacao_mesma_empresa_atualiza(self):
        confirmar_importacao(
            self.criar_importacao(
                self.empresa_a,
                descricao="Original",
                valor="100,00",
            )
        )

        segunda = self.criar_importacao(
            self.empresa_a,
            descricao="Atualizado",
            valor="150,00",
        )

        confirmar_importacao(
            segunda
        )

        self.assertEqual(
            Lancamento.objects.filter(
                empresa=self.empresa_a,
                numero_lancamento="HOM-LANC-001",
            ).count(),
            1,
        )

        lancamento = Lancamento.objects.get(
            empresa=self.empresa_a,
            numero_lancamento="HOM-LANC-001",
        )

        self.assertEqual(
            lancamento.descricao,
            "Atualizado",
        )

        self.assertEqual(
            str(lancamento.valor_documento),
            "150.00",
        )

        segunda.refresh_from_db()

        self.assertEqual(
            segunda.total_novos,
            0,
        )

        self.assertEqual(
            segunda.total_atualizados,
            1,
        )

    def test_empresa_inexistente_nao_e_criada(self):
        importacao = Importacao.objects.create(
            tipo="lancamento",
            arquivo_nome="empresa_inexistente.csv",
            criado_por=self.user,
            total_lido=1,
            linhas=[
                {
                    "empresa": "OSC INEXISTENTE",
                    "numtermo": "HOM-LANC-TC",
                    "prestacao_numero": "HOM-LANC-PC",
                    "competencia_ano": "2026",
                    "competencia_mes": "1",
                    "numero_lancamento": "HOM-LANC-002",
                    "data_documento": "15/01/2026",
                    "descricao": "Teste",
                    "valor_documento": "100,00",
                }
            ],
        )

        confirmar_importacao(
            importacao
        )

        importacao.refresh_from_db()

        self.assertEqual(
            importacao.total_erros,
            1,
        )

        self.assertFalse(
            Empresa.objects.filter(
                nome="OSC INEXISTENTE"
            ).exists()
        )

        self.assertFalse(
            Lancamento.objects.filter(
                numero_lancamento="HOM-LANC-002"
            ).exists()
        )

    def test_prestacao_de_outro_termo_nao_e_aceita(self):
        outro_termo = Termos.objects.create(
            empresa=self.empresa_a,
            numtermo="OUTRO-TC",
            termo="Outro Termo",
        )

        outra_prestacao = Prestacao.objects.create(
            empresa=self.empresa_a,
            termo=outro_termo,
            tipo="cnpj",
            numtermo="OUTRA-PC",
        )

        importacao = self.criar_importacao(
            self.empresa_a
        )

        importacao.linhas[0][
            "prestacao_numero"
        ] = outra_prestacao.numtermo

        importacao.save(
            update_fields=["linhas"]
        )

        confirmar_importacao(
            importacao
        )

        importacao.refresh_from_db()

        self.assertEqual(
            importacao.total_erros,
            1,
        )

        self.assertFalse(
            Lancamento.objects.filter(
                empresa=self.empresa_a,
                numero_lancamento="HOM-LANC-001",
            ).exists()
        )

    def test_competencia_inexistente_nao_cria_lancamento(self):
        importacao = self.criar_importacao(
            self.empresa_a
        )

        importacao.linhas[0][
            "competencia_mes"
        ] = "2"

        importacao.save(
            update_fields=["linhas"]
        )

        confirmar_importacao(
            importacao
        )

        importacao.refresh_from_db()

        self.assertEqual(
            importacao.total_erros,
            1,
        )

        self.assertFalse(
            Lancamento.objects.filter(
                empresa=self.empresa_a,
                numero_lancamento="HOM-LANC-001",
            ).exists()
        )
