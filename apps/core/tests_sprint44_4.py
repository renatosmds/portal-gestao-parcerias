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


class PGPRulesRHSprint444Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC RH Sprint 44.4"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RH444/26",
            termo="Termo RH 44.4",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
        )

        self.user = User.objects.create_user(
            username="rh444"
        )

        self.funcionario = Funcionario.objects.create(
            nome="Trabalhador RH 44.4",
            usuario="rh444",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Cidade ficticia",
            estado="MG",
            email="rh444@example.invalid",
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
            imagem="funcionarios/rh444.jpg",
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

    def criar_folha(
        self,
        inss=Decimal("300.00"),
    ):
        return FolhaPagamento.objects.create(
            funcionario=self.funcionario,
            folha_ponto=self.ponto,
            competencia=date(2026, 7, 1),
            salario_base=Decimal("3000.00"),
            inss=inss,
            status="fechada",
        )

    def test_inss_divergente_gera_alerta(self):
        folha = self.criar_folha(
            inss=Decimal("350.00")
        )

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_INSS_DIVERGENTE",
            codigos,
        )

    def test_inss_compativel_nao_gera_divergencia(self):
        folha = self.criar_folha(
            inss=Decimal("300.00")
        )

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertNotIn(
            "RH_INSS_DIVERGENTE",
            codigos,
        )

    def test_fgts_nao_informado_em_clt_gera_alerta(self):
        self.funcionario.fgts = None
        self.funcionario.save(
            update_fields=["fgts"]
        )

        folha = self.criar_folha()

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_FGTS_NAO_INFORMADO",
            codigos,
        )

    def test_encargos_nao_alteram_folha(self):
        folha = self.criar_folha(
            inss=Decimal("350.00")
        )

        status_antes = folha.status
        salario_antes = folha.salario_base
        inss_antes = folha.inss

        motor_regras.analisar_folha_pagamento(
            folha
        )

        folha.refresh_from_db()

        self.assertEqual(
            folha.status,
            status_antes,
        )

        self.assertEqual(
            folha.salario_base,
            salario_antes,
        )

        self.assertEqual(
            folha.inss,
            inss_antes,
        )
