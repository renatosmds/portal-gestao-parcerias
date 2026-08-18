from datetime import date
from decimal import Decimal

from django.db import models
from django.test import TestCase

from apps.empresas.models import Empresa
from apps.lancamentos.models import Lancamento
from apps.metas.models import MetaExecucao
from apps.planos_trabalho.models import (
    ItemPlanoTrabalho,
    PlanoTrabalho,
)
from apps.planos_trabalho.vinculos import (
    vincular_lancamento_item,
)
from apps.prestacao.models import Prestacao
from apps.regras.engine import motor_regras
from apps.termos.models import Termos


class PlanoTrabalhoSprint458Tests(TestCase):

    def criar_prestacao(
        self,
        *,
        empresa,
        numtermo,
    ):
        kwargs = {
            "empresa": empresa,
            "numtermo": numtermo,
        }

        for campo in Prestacao._meta.fields:
            if (
                campo.primary_key
                or campo.name in kwargs
            ):
                continue

            if campo.has_default():
                continue

            if campo.null:
                continue

            if isinstance(
                campo,
                models.ForeignKey,
            ):
                continue

            if isinstance(
                campo,
                (
                    models.CharField,
                    models.TextField,
                    models.FileField,
                ),
            ):
                kwargs[campo.name] = ""

            elif isinstance(
                campo,
                models.BooleanField,
            ):
                kwargs[campo.name] = False

            elif isinstance(
                campo,
                models.IntegerField,
            ):
                kwargs[campo.name] = 0

            elif isinstance(
                campo,
                models.FloatField,
            ):
                kwargs[campo.name] = 0.0

            elif isinstance(
                campo,
                models.DecimalField,
            ):
                kwargs[campo.name] = Decimal(
                    "0"
                )

            elif isinstance(
                campo,
                models.DateField,
            ):
                kwargs[campo.name] = date(
                    2026,
                    1,
                    1,
                )

        return Prestacao.objects.create(
            **kwargs
        )

    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="OSC Sprint 45.8"
        )

        self.termo = Termos.objects.create(
            empresa=self.empresa,
            numtermo="PT458/26",
            termo="Termo Sprint 45.8",
            objeto=(
                "Atendimento socioassistencial "
                "a famílias em situação de "
                "vulnerabilidade social"
            ),
        )

        self.prestacao = self.criar_prestacao(
            empresa=self.empresa,
            numtermo="PT458/26",
        )

        self.meta = MetaExecucao.objects.create(
            prestacao=self.prestacao,
            codigo="META-458",
            titulo=(
                "Atendimento às famílias"
            ),
            descricao=(
                "Realizar atendimento "
                "socioassistencial às famílias "
                "em vulnerabilidade social"
            ),
            unidade="numero",
            valor_previsto=Decimal("100.00"),
            valor_realizado=Decimal("25.00"),
            inicio=date(2026, 1, 1),
            fim=date(2026, 12, 31),
        )

        self.plano = PlanoTrabalho.objects.create(
            termo=self.termo,
            versao=1,
            titulo="Plano Sprint 45.8",
            origem=PlanoTrabalho.Origem.INICIAL,
            situacao=PlanoTrabalho.Situacao.VIGENTE,
            inicio_vigencia=date(2026, 1, 1),
            fim_vigencia=date(2026, 12, 31),
            data_eficacia=date(2026, 1, 1),
        )

        self.item = ItemPlanoTrabalho.objects.create(
            plano=self.plano,
            codigo="ITEM-458",
            rubrica_nivel_1="Custeio",
            descricao=(
                "Material para atendimento "
                "das famílias"
            ),
            valor_total_previsto=Decimal(
                "10000.00"
            ),
            meta=self.meta,
        )

        self.lancamento = Lancamento.objects.create(
            empresa=self.empresa,
            termo=self.termo,
            numero_lancamento="458-001",
            tipo_documento=(
                Lancamento.TipoDocumento.NFE
            ),
            numero_documento="NF-458",
            data_documento=date(
                2026,
                5,
                10,
            ),
            data_pagamento=date(
                2026,
                5,
                15,
            ),
            descricao=(
                "Material para atendimento "
                "das famílias"
            ),
            valor_documento=Decimal(
                "500.00"
            ),
        )

        vincular_lancamento_item(
            self.lancamento,
            self.item,
        )

    def codigos(self, resultado):
        return {
            achado.codigo
            for achado
            in resultado.achados
        }

    def test_rastreabilidade_meta_termo_confirmada(self):
        resultado = (
            motor_regras
            .analisar_meta_objeto_item(
                self.item
            )
        )

        self.assertIn(
            "PT_META_RASTREABILIDADE_CONFIRMADA",
            self.codigos(resultado),
        )

        self.assertFalse(
            resultado.criticos
        )

    def test_item_sem_meta_gera_alerta(self):
        self.item.meta = None
        self.item.save(
            update_fields=["meta"]
        )

        resultado = (
            motor_regras
            .analisar_meta_objeto_item(
                self.item
            )
        )

        self.assertIn(
            "PT_ITEM_SEM_META_VINCULADA",
            self.codigos(resultado),
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "requer_conferencia",
        )

    def test_meta_de_outra_empresa_gera_critico(self):
        outra_empresa = (
            Empresa.objects.create(
                nome="Outra OSC Sprint 45.8"
            )
        )

        outra_prestacao = (
            self.criar_prestacao(
                empresa=outra_empresa,
                numtermo="PT458/26",
            )
        )

        outra_meta = (
            MetaExecucao.objects.create(
                prestacao=outra_prestacao,
                codigo="META-OUTRA",
                titulo="Outra meta",
                descricao="Outra execução",
                unidade="numero",
                valor_previsto=Decimal(
                    "10.00"
                ),
            )
        )

        self.item.meta = outra_meta
        self.item.save(
            update_fields=["meta"]
        )

        resultado = (
            motor_regras
            .analisar_meta_objeto_item(
                self.item
            )
        )

        self.assertIn(
            "PT_META_EMPRESA_INCOMPATIVEL",
            self.codigos(resultado),
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_meta_de_outro_termo_gera_critico(self):
        outra_prestacao = (
            self.criar_prestacao(
                empresa=self.empresa,
                numtermo="OUTRO-458/26",
            )
        )

        outra_meta = (
            MetaExecucao.objects.create(
                prestacao=outra_prestacao,
                codigo="META-OUTRO-TERMO",
                titulo="Atendimento",
                descricao="Atendimento social",
                unidade="numero",
                valor_previsto=Decimal(
                    "10.00"
                ),
            )
        )

        self.item.meta = outra_meta
        self.item.save(
            update_fields=["meta"]
        )

        resultado = (
            motor_regras
            .analisar_meta_objeto_item(
                self.item
            )
        )

        self.assertIn(
            "PT_META_TERMO_INCOMPATIVEL",
            self.codigos(resultado),
        )

        self.assertEqual(
            resultado.resultado_preliminar,
            "pendencia_critica",
        )

    def test_termo_sem_objeto_gera_alerta(self):
        self.termo.objeto = ""
        self.termo.save(
            update_fields=["objeto"]
        )

        resultado = (
            motor_regras
            .analisar_meta_objeto_item(
                self.item
            )
        )

        self.assertIn(
            "PT_TERMO_SEM_OBJETO_ESTRUTURADO",
            self.codigos(resultado),
        )

    def test_divergencia_textual_nao_aplica_glosa(self):
        self.meta.titulo = (
            "Plantio de mudas"
        )

        self.meta.descricao = (
            "Recuperação de área ambiental "
            "com espécies nativas"
        )

        self.meta.save(
            update_fields=[
                "titulo",
                "descricao",
            ]
        )

        situacao_antes = (
            self.lancamento.situacao
        )

        tipo_glosa_antes = (
            self.lancamento.tipo_glosa
        )

        valor_glosa_antes = (
            self.lancamento.valor_glosa
        )

        resultado = (
            motor_regras
            .analisar_meta_objeto_item(
                self.item
            )
        )

        self.assertIn(
            "PT_DESPESA_META_SEM_EVIDENCIA_TEXTUAL",
            self.codigos(resultado),
        )

        self.assertIn(
            "PT_META_OBJETO_SEM_EVIDENCIA_TEXTUAL",
            self.codigos(resultado),
        )

        self.assertFalse(
            resultado.criticos
        )

        self.lancamento.refresh_from_db()

        self.assertEqual(
            self.lancamento.situacao,
            situacao_antes,
        )

        self.assertEqual(
            self.lancamento.tipo_glosa,
            tipo_glosa_antes,
        )

        self.assertEqual(
            self.lancamento.valor_glosa,
            valor_glosa_antes,
        )
