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


class PGPRulesRHSprint442Tests(TestCase):

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC RH Sprint 44"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="RH44/2026",
            termo="Termo RH 44",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
            valorglobal=Decimal("100000.00"),
        )

        self.user = User.objects.create_user(
            username="rh_sprint44"
        )

        self.funcionario = Funcionario.objects.create(
            nome="Trabalhador Teste",
            usuario="trabalhador_teste",
            endereco="Endereco ficticio",
            bairro="Bairro ficticio",
            cep="00000-000",
            cidade="Cidade ficticia",
            estado="MG",
            email="teste@example.invalid",
            Telefone="000000000",
            salarioBase=Decimal("3000.00"),
            fgts=Decimal("240.00"),
            cpf="000.000.000-00",
            tipo_vinculo="clt",
            data_admissao=date(2026, 1, 1),
            jornada_semanal=Decimal("44.00"),
            divisor_mensal=220,
            termo=self.termo,
            empresa=self.empresa,
            user=self.user,
            imagem="funcionarios/teste.jpg",
        )

    def criar_ponto(
        self,
        funcionario=None,
        competencia=date(2026, 7, 1),
    ):
        return FolhaPonto.objects.create(
            funcionario=funcionario or self.funcionario,
            competencia=competencia,
            horas_previstas=Decimal("176.00"),
            horas_trabalhadas=Decimal("176.00"),
            horas_extras=Decimal("0.00"),
            horas_faltas_atrasos=Decimal("0.00"),
            banco_horas=Decimal("0.00"),
            status="fechada",
        )

    def criar_folha(
        self,
        ponto=None,
        competencia=date(2026, 7, 1),
    ):
        return FolhaPagamento.objects.create(
            funcionario=self.funcionario,
            folha_ponto=ponto,
            competencia=competencia,
            salario_base=Decimal("3000.00"),
            status="fechada",
        )

    def test_folha_estruturalmente_regular(self):
        ponto = self.criar_ponto()
        folha = self.criar_folha(ponto=ponto)

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        self.assertEqual(
            resultado.total_achados,
            0,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "sem_inconsistencia_detectada",
        )

    def test_funcionario_sem_termo_requer_conferencia(self):
        self.funcionario.termo = None
        self.funcionario.save(
            update_fields=["termo"]
        )

        ponto = self.criar_ponto()
        folha = self.criar_folha(ponto=ponto)

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_FUNC_SEM_TERMO",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "requer_conferencia",
        )

    def test_competencia_ponto_divergente_e_critica(self):
        ponto = self.criar_ponto(
            competencia=date(2026, 6, 1)
        )

        folha = self.criar_folha(
            ponto=ponto,
            competencia=date(2026, 7, 1),
        )

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_COMPETENCIA_PONTO_DIVERGENTE",
            codigos,
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_empresa_do_termo_divergente_e_critica(self):
        outra_empresa = Empresa.objects.create(
            nome="Outra OSC Sprint 44"
        )

        outro_termo = Termos.objects.create(
            empresa=outra_empresa,
            numtermo="OUT44/26",
            termo="Outro Termo RH",
            inicioVigencia="01/01/2026",
            terminoVigencia="31/12/2026",
        )

        self.funcionario.termo = outro_termo
        self.funcionario.save(
            update_fields=["termo"]
        )

        ponto = self.criar_ponto()
        folha = self.criar_folha(ponto=ponto)

        resultado = motor_regras.analisar_folha_pagamento(
            folha
        )

        codigos = {
            item.codigo
            for item in resultado.achados
        }

        self.assertIn(
            "RH_EMPRESA_TERMO_DIVERGENTE",
            codigos,
        )

    def test_motor_rh_nao_altera_folha(self):
        ponto = self.criar_ponto(
            competencia=date(2026, 6, 1)
        )

        folha = self.criar_folha(
            ponto=ponto,
            competencia=date(2026, 7, 1),
        )

        salario_antes = folha.salario_base
        status_antes = folha.status
        observacoes_antes = folha.observacoes

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

        self.assertEqual(
            folha.observacoes,
            observacoes_antes,
        )

