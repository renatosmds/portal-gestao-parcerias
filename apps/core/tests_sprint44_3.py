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


class PGPRulesRHSprint443Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC RH Sprint 44.3"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RH443/26",
            termo="Termo RH 44.3",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
        )

        self.user = User.objects.create_user(
            username="rh443"
        )

        self.funcionario = Funcionario.objects.create(
            nome="Trabalhador RH 44.3",
            usuario="rh443",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Cidade ficticia",
            estado="MG",
            email="rh443@example.invalid",
            Telefone="000000000",
            salarioBase=Decimal("3000.00"),
            tipo_vinculo="clt",
            data_admissao=date(2026, 1, 1),
            divisor_mensal=220,
            termo=self.termo,
            empresa=self.empresa,
            user=self.user,
            imagem="funcionarios/rh443.jpg",
        )

    def criar_ponto(
        self,
        horas_previstas=Decimal("176.00"),
        horas_trabalhadas=Decimal("176.00"),
        horas_extras=Decimal("0.00"),
        horas_faltas=Decimal("0.00"),
    ):
        return FolhaPonto.objects.create(
            funcionario=self.funcionario,
            competencia=date(2026, 7, 1),
            horas_previstas=horas_previstas,
            horas_trabalhadas=horas_trabalhadas,
            horas_extras=horas_extras,
            horas_faltas_atrasos=horas_faltas,
            banco_horas=Decimal("0.00"),
            status="fechada",
        )

    def criar_folha(
        self,
        ponto,
        salario=Decimal("3000.00"),
    ):
        return FolhaPagamento.objects.create(
            funcionario=self.funcionario,
            folha_ponto=ponto,
            competencia=date(2026, 7, 1),
            salario_base=salario,
            status="fechada",
        )

    def test_salario_base_divergente_gera_achado(self):
        ponto = self.criar_ponto()

        folha = self.criar_folha(
            ponto,
            salario=Decimal("3200.00"),
        )

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_SALARIO_BASE_DIVERGENTE",
            codigos,
        )

    def test_falta_com_desconto_gera_informativo(self):
        ponto = self.criar_ponto(
            horas_trabalhadas=Decimal("168.00"),
            horas_faltas=Decimal("8.00"),
        )

        folha = self.criar_folha(ponto)

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_FALTA_COM_DESCONTO",
            codigos,
        )

        achado = next(
            item
            for item in resultado.achados
            if item.codigo == "RH_FALTA_COM_DESCONTO"
        )

        self.assertEqual(
            achado.resultado,
            "informativo",
        )

    def test_horas_nao_conciliadas_geram_alerta(self):
        ponto = self.criar_ponto(
            horas_previstas=Decimal("176.00"),
            horas_trabalhadas=Decimal("160.00"),
            horas_faltas=Decimal("8.00"),
        )

        folha = self.criar_folha(ponto)

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_HORAS_NAO_CONCILIADAS",
            codigos,
        )

    def test_falta_nao_implica_glosa_automatica(self):
        ponto = self.criar_ponto(
            horas_trabalhadas=Decimal("168.00"),
            horas_faltas=Decimal("8.00"),
        )

        folha = self.criar_folha(ponto)

        salario_antes = folha.salario_base
        status_antes = folha.status

        motor_regras.analisar_folha_pagamento(
            folha
        )

        folha.refresh_from_db()

        self.assertEqual(
            folha.salario_base,
            salario_antes,
        )

        self.assertEqual(
            folha.status,
            status_antes,
        )
