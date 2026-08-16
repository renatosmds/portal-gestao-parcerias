from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    FolhaPagamento,
    FolhaPonto,
    Funcionario,
)
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PGPRulesRHSprint445Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC RH Sprint 44.5"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RH445/26",
            termo="Termo RH 44.5",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
        )

        self.user = User.objects.create_user(
            username="rh445"
        )

        self.funcionario = Funcionario.objects.create(
            nome="Trabalhador RH 44.5",
            usuario="rh445",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Cidade ficticia",
            estado="MG",
            email="rh445@example.invalid",
            Telefone="000000000",
            salarioBase=Decimal("3000.00"),
            fgts=Decimal("240.00"),
            inss=Decimal("300.00"),
            tipo_vinculo="clt",
            data_admissao=date(2026, 1, 1),
            divisor_mensal=220,
            termo=self.termo,
            empresa=self.empresa,
            user=self.user,
            imagem="funcionarios/rh445.jpg",
        )

        self.ponto = FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(2026, 7, 1),
            horas_previstas=Decimal("176.00"),
            horas_trabalhadas=Decimal("176.00"),
            horas_extras=Decimal("0.00"),
            horas_faltas_atrasos=Decimal("0.00"),
            banco_horas=Decimal("0.00"),
            status="fechada",
        )

        self.folha = FolhaPagamento.objects.create(
            funcionario=self.funcionario,
            folha_ponto=self.ponto,
            competencia=date(2026, 7, 1),
            salario_base=Decimal("3000.00"),
            inss=Decimal("300.00"),
            status="fechada",
        )

    def criar_documento(
        self,
        tipo,
        descricao,
        *,
        funcionario=True,
        empresa=None,
        termo=None,
        status=Documento.Status.CONFERIDO,
    ):
        return Documento.objects.create(
            descricao=descricao,
            arquivo=f"documentos/{descricao}.pdf",
            pertence=self.funcionario if funcionario else None,
            empresa=self.empresa if empresa is None else empresa,
            termo=self.termo if termo is None else termo,
            tipo=tipo,
            status=status,
            documento_legivel=True,
            dados_compativeis=True,
            vigencia_valida=True,
            pagamento_comprovado=True,
            atesto_valido=True,
        )

    def test_ausencia_documental_gera_pendencias(self):
        resultado = motor_regras.analisar_documentacao_rh(
            self.folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_DOC_FOLHA_NAO_LOCALIZADA",
            codigos,
        )

        self.assertIn(
            "RH_DOC_PAGAMENTO_NAO_LOCALIZADO",
            codigos,
        )

        self.assertIn(
            "RH_DOC_GUIA_NAO_LOCALIZADA",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "documentacao_incompleta",
        )

    def test_documentacao_completa_nao_gera_pendencia(self):
        self.criar_documento(
            Documento.Tipo.FOLHA,
            "folha445",
        )

        self.criar_documento(
            Documento.Tipo.COMPROVANTE,
            "pagamento445",
        )

        self.criar_documento(
            Documento.Tipo.GUIA,
            "guia445",
        )

        resultado = motor_regras.analisar_documentacao_rh(
            self.folha
        )

        self.assertEqual(
            resultado.total_achados,
            0,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "documentacao_localizada",
        )

    def test_guia_coletiva_e_tratada_como_candidata(self):
        self.criar_documento(
            Documento.Tipo.FOLHA,
            "folha_coletiva445",
        )

        self.criar_documento(
            Documento.Tipo.COMPROVANTE,
            "pagamento_coletivo445",
        )

        self.criar_documento(
            Documento.Tipo.GUIA,
            "guia_coletiva445",
            funcionario=False,
        )

        resultado = motor_regras.analisar_documentacao_rh(
            self.folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_GUIA_COLETIVA_CANDIDATA",
            codigos,
        )

        self.assertNotIn(
            "RH_DOC_GUIA_NAO_LOCALIZADA",
            codigos,
        )

    def test_documento_de_outra_empresa_e_critico(self):
        outra_empresa = Empresa.objects.create(
            nome="Outra OSC RH 44.5"
        )

        self.criar_documento(
            Documento.Tipo.FOLHA,
            "folha_empresa_errada445",
            empresa=outra_empresa,
        )

        resultado = motor_regras.analisar_documentacao_rh(
            self.folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_DOC_EMPRESA_DIVERGENTE",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_analise_documental_nao_altera_registros(self):
        self.criar_documento(
            Documento.Tipo.FOLHA,
            "folha_preserva445",
            status=Documento.Status.COM_PENDENCIA,
        )

        salario_antes = self.folha.salario_base
        status_antes = self.folha.status

        motor_regras.analisar_documentacao_rh(
            self.folha
        )

        self.folha.refresh_from_db()

        self.assertEqual(
            self.folha.salario_base,
            salario_antes,
        )

        self.assertEqual(
            self.folha.status,
            status_antes,
        )
