from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.core.models import SequenciaPseudonimo
from apps.fornecedores.models import Fornecedores
from apps.funcionarios.models import Funcionario


class PseudonimizacaoTestCase(TestCase):

    def setUp(self):
        SequenciaPseudonimo.objects.update_or_create(
            tipo=SequenciaPseudonimo.Tipo.COLABORADOR,
            defaults={"ultimo_numero": 0},
        )

        SequenciaPseudonimo.objects.update_or_create(
            tipo=SequenciaPseudonimo.Tipo.FORNECEDOR,
            defaults={"ultimo_numero": 0},
        )

    def novo_funcionario(self, cpf, nome="Colaborador Teste"):
        return Funcionario(
            nome=nome,
            usuario="teste",
            endereco="Rua Teste",
            bairro="Centro",
            cep="00000-000",
            cidade="Contagem",
            estado="MG",
            email="teste@example.com",
            Telefone="000000000",
            cpf=cpf,
        )

    def novo_fornecedor(
        self,
        numero,
        tipo="cnpj",
        credor="Fornecedor Teste",
    ):
        return Fornecedores(
            credor=credor,
            pessoa=(
                "jurídica"
                if tipo == "cnpj"
                else "física"
            ),
            tipo=tipo,
            numero=numero,
        )

    def test_cpf_invalido_nao_consume_codigo(self):
        funcionario = self.novo_funcionario(
            "111.111.111-11"
        )

        with self.assertRaises(ValidationError):
            funcionario.save()

        sequencia = SequenciaPseudonimo.objects.get(
            tipo=SequenciaPseudonimo.Tipo.COLABORADOR
        )

        self.assertEqual(
            sequencia.ultimo_numero,
            0,
        )

    def test_cpf_valido_gera_primeiro_col(self):
        funcionario = self.novo_funcionario(
            "529.982.247-25"
        )

        funcionario.save()

        self.assertEqual(
            funcionario.codigo_pseudonimo,
            "COL-000001",
        )

        self.assertEqual(
            funcionario.cpf_normalizado,
            "52998224725",
        )

    def test_cpf_duplicado_nao_gera_outro_col(self):
        primeiro = self.novo_funcionario(
            "529.982.247-25",
            nome="Primeiro",
        )
        primeiro.save()

        segundo = self.novo_funcionario(
            "52998224725",
            nome="Segundo",
        )

        with self.assertRaises(ValidationError):
            segundo.save()

        sequencia = SequenciaPseudonimo.objects.get(
            tipo=SequenciaPseudonimo.Tipo.COLABORADOR
        )

        self.assertEqual(
            sequencia.ultimo_numero,
            1,
        )

    def test_codigo_col_permanece_apos_edicao(self):
        funcionario = self.novo_funcionario(
            "529.982.247-25"
        )
        funcionario.save()

        codigo = funcionario.codigo_pseudonimo

        funcionario.nome = "Nome Alterado"
        funcionario.tipo_vinculo = "estagiario"
        funcionario.save()

        funcionario.refresh_from_db()

        self.assertEqual(
            funcionario.codigo_pseudonimo,
            codigo,
        )

    def test_cpf_associado_ao_col_nao_pode_ser_trocado(self):
        funcionario = self.novo_funcionario(
            "529.982.247-25"
        )
        funcionario.save()

        funcionario.cpf = "111.444.777-35"

        with self.assertRaises(ValidationError):
            funcionario.save()

    def test_user_pode_ser_nulo(self):
        funcionario = self.novo_funcionario(
            "529.982.247-25"
        )

        funcionario.user = None
        funcionario.save()

        self.assertIsNone(
            funcionario.user,
        )

        self.assertEqual(
            funcionario.codigo_pseudonimo,
            "COL-000001",
        )

    def test_cnpj_invalido_nao_consume_codigo(self):
        fornecedor = self.novo_fornecedor(
            "11.111.111/1111-11"
        )

        with self.assertRaises(ValidationError):
            fornecedor.save()

        sequencia = SequenciaPseudonimo.objects.get(
            tipo=SequenciaPseudonimo.Tipo.FORNECEDOR
        )

        self.assertEqual(
            sequencia.ultimo_numero,
            0,
        )

    def test_cnpj_valido_gera_primeiro_for(self):
        fornecedor = self.novo_fornecedor(
            "04.252.011/0001-10"
        )

        fornecedor.save()

        self.assertEqual(
            fornecedor.codigo_pseudonimo,
            "FOR-000001",
        )

        self.assertEqual(
            fornecedor.documento_normalizado,
            "04252011000110",
        )

    def test_cnpj_duplicado_nao_gera_outro_for(self):
        primeiro = self.novo_fornecedor(
            "04.252.011/0001-10",
            credor="Primeiro",
        )
        primeiro.save()

        segundo = self.novo_fornecedor(
            "04252011000110",
            credor="Segundo",
        )

        with self.assertRaises(ValidationError):
            segundo.save()

        sequencia = SequenciaPseudonimo.objects.get(
            tipo=SequenciaPseudonimo.Tipo.FORNECEDOR
        )

        self.assertEqual(
            sequencia.ultimo_numero,
            1,
        )

    def test_codigo_for_permanece_apos_edicao(self):
        fornecedor = self.novo_fornecedor(
            "04.252.011/0001-10"
        )

        fornecedor.save()

        codigo = fornecedor.codigo_pseudonimo

        fornecedor.credor = "Fornecedor Alterado"
        fornecedor.razao = "Razao Alterada"
        fornecedor.save()

        fornecedor.refresh_from_db()

        self.assertEqual(
            fornecedor.codigo_pseudonimo,
            codigo,
        )

    def test_fornecedor_pf_aceita_cpf_valido(self):
        fornecedor = self.novo_fornecedor(
            "529.982.247-25",
            tipo="cpf",
        )

        fornecedor.save()

        self.assertEqual(
            fornecedor.codigo_pseudonimo,
            "FOR-000001",
        )

        self.assertEqual(
            fornecedor.documento_normalizado,
            "52998224725",
        )
