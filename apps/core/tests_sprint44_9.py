from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.funcionarios.models import Funcionario
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PGPRulesRHSprint449Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC RH Sprint 44.9"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RH449/26",
            termo="Termo RH 44.9",
        )

        self.user = User.objects.create_user(
            username="rh449"
        )

        self.funcionario = Funcionario.objects.create(
            nome="Trabalhador RH 44.9",
            usuario="rh449",
            endereco="Rua Ficticia 100",
            bairro="Bairro Ficticio",
            cep="00000-000",
            cidade="Cidade Ficticia",
            estado="MG",
            email="rh449@example.invalid",
            Telefone="31999999999",
            cpf="000.000.000-00",
            pis_pasep_nit="00000000000",
            data_nascimento=date(1990, 1, 1),
            banco="000",
            agencia="0001",
            conta_bancaria="12345-6",
            salarioBase=Decimal("3000.00"),
            tipo_vinculo="clt",
            termo=self.termo,
            empresa=self.empresa,
            user=self.user,
            imagem="funcionarios/rh449.jpg",
        )

    def test_identifica_categorias_sem_expor_valores(self):
        resultado = motor_regras.analisar_lgpd_rh(
            self.funcionario
        )

        texto_evidencias = " ".join(
            item.evidencia
            for item in resultado.achados
        )

        self.assertIn(
            "LGPD_RH_DADOS_PESSOAIS",
            {
                item.codigo
                for item in resultado.achados
            },
        )

        self.assertNotIn(
            self.funcionario.cpf,
            texto_evidencias,
        )

        self.assertNotIn(
            self.funcionario.conta_bancaria,
            texto_evidencias,
        )

    def test_dados_bancarios_nao_sao_rotulados_como_sensiveis(self):
        resultado = motor_regras.analisar_lgpd_rh(
            self.funcionario
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "LGPD_RH_DADOS_FINANCEIROS",
            codigos,
        )

        self.assertNotIn(
            "LGPD_RH_DOC_POTENCIALMENTE_SENSIVEL",
            codigos,
        )

    def test_atestado_e_sinalizado_como_potencialmente_sensivel(self):
        Documento.objects.create(
            descricao="Atestado medico",
            arquivo="documentos/atestado449.pdf",
            pertence=self.funcionario,
            empresa=self.empresa,
            termo=self.termo,
            tipo=Documento.Tipo.OUTRO,
        )

        resultado = motor_regras.analisar_lgpd_rh(
            self.funcionario
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "LGPD_RH_DOC_POTENCIALMENTE_SENSIVEL",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "risco_elevado_privacidade",
        )

    def test_ia_sem_minimizacao_gera_critico(self):
        resultado = motor_regras.analisar_lgpd_rh(
            self.funcionario,
            uso_ia=True,
            dados_minimizados=False,
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "LGPD_RH_IA_SEM_MINIMIZACAO",
            codigos,
        )

    def test_ia_minimizada_nao_gera_alerta_de_ia_sem_minimizacao(self):
        resultado = motor_regras.analisar_lgpd_rh(
            self.funcionario,
            uso_ia=True,
            dados_minimizados=True,
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "LGPD_RH_IA_MINIMIZADA",
            codigos,
        )

        self.assertNotIn(
            "LGPD_RH_IA_SEM_MINIMIZACAO",
            codigos,
        )
