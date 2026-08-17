from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.funcionarios.models import (
    FolhaPagamento,
    FolhaPonto,
    Funcionario,
)
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PGPRulesRHSprint448Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC RH Sprint 44.8"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RH448/26",
            termo="Termo RH 44.8",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
        )

        self.user = User.objects.create_user(
            username="rh448"
        )

        self.funcionario = Funcionario.objects.create(
            nome="Trabalhador RH 44.8",
            usuario="rh448",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Cidade ficticia",
            estado="MG",
            email="rh448@example.invalid",
            Telefone="000000000",
            salarioBase=Decimal("3000.00"),
            fgts=Decimal("240.00"),
            tipo_vinculo="clt",
            data_admissao=date(2026, 1, 1),
            termo=self.termo,
            empresa=self.empresa,
            user=self.user,
            imagem="funcionarios/rh448.jpg",
        )

        self.ponto = FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(2026, 7, 1),
            horas_previstas=Decimal("176.00"),
            horas_trabalhadas=Decimal("176.00"),
            horas_extras=Decimal("0.00"),
            horas_faltas_atrasos=Decimal("0.00"),
            status="fechada",
        )

        self.folha = FolhaPagamento.objects.create(
            funcionario=self.funcionario,
            folha_ponto=self.ponto,
            competencia=date(2026, 7, 1),
            salario_base=Decimal("3000.00"),
            status="fechada",
        )

    def codigos(self):
        resultado = motor_regras.analisar_verbas_rh(
            self.folha
        )

        return resultado, {
            item.codigo
            for item in resultado.achados
        }

    def test_rescisao_sem_desligamento_gera_alerta(self):
        self.funcionario.avisoPrevio = Decimal("3000.00")
        self.funcionario.save(
            update_fields=["avisoPrevio"]
        )

        resultado, codigos = self.codigos()

        self.assertIn(
            "RH_VERBA_RESCISORIA_SEM_DESLIGAMENTO",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "requer_conferencia",
        )

    def test_ferias_sem_terco_gera_alerta(self):
        self.funcionario.avosFerias = Decimal("1000.00")
        self.funcionario.avosTercoFerias = Decimal("0.00")

        self.funcionario.save(
            update_fields=[
                "avosFerias",
                "avosTercoFerias",
            ]
        )

        resultado, codigos = self.codigos()

        self.assertIn(
            "RH_FERIAS_SEM_TERCO_IDENTIFICADO",
            codigos,
        )

    def test_desligamento_antes_admissao_e_critico(self):
        self.funcionario.data_admissao = date(2026, 7, 10)
        self.funcionario.data_desligamento = date(2026, 7, 5)

        self.funcionario.save(
            update_fields=[
                "data_admissao",
                "data_desligamento",
            ]
        )

        resultado, codigos = self.codigos()

        self.assertIn(
            "RH_DESLIGAMENTO_ANTES_ADMISSAO",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_vinculo_sem_sobreposicao_com_termo_e_critico(self):
        self.funcionario.data_admissao = date(2025, 1, 1)
        self.funcionario.data_desligamento = date(2025, 12, 20)
        self.funcionario.avisoPrevio = Decimal("3000.00")

        self.funcionario.save(
            update_fields=[
                "data_admissao",
                "data_desligamento",
                "avisoPrevio",
            ]
        )

        resultado, codigos = self.codigos()

        self.assertIn(
            "RH_RESCISAO_SEM_SOBREPOSICAO_TERMO",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_total_e_componentes_nao_sao_somados_automaticamente(self):
        self.funcionario.data_desligamento = date(2026, 7, 20)
        self.funcionario.avisoPrevio = Decimal("1000.00")
        self.funcionario.avosFerias = Decimal("500.00")
        self.funcionario.avosTercoFerias = Decimal("166.67")
        self.funcionario.avos13Salario = Decimal("500.00")
        self.funcionario.totalVerbaRescisoria = Decimal("2166.67")

        self.funcionario.save(
            update_fields=[
                "data_desligamento",
                "avisoPrevio",
                "avosFerias",
                "avosTercoFerias",
                "avos13Salario",
                "totalVerbaRescisoria",
            ]
        )

        resultado, codigos = self.codigos()

        self.assertIn(
            "RH_RESCISAO_TOTAL_E_COMPONENTES_PRESENTES",
            codigos,
        )

        self.assertTrue(
            all(
                item.resultado != "glosa"
                for item in resultado.achados
            )
        )
