from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import (
    DecisaoJustificativa,
    DiaFolhaPonto,
    FolhaPonto,
    Funcionario,
    JustificativaPonto,
    MovimentoBancoHoras,
    RegimeBancoHoras,
    TipoJustificativa,
)

from .services import (
    apurar_dia_folha_ponto,
    horas_falta_para_folha_dia,
    tratar_saldo_dia,
    validar_competencia_pronta_para_fechamento,
)

from .services_justificativas import (
    criar_justificativa,
    registrar_decisao,
    resumo_decisoes_dia,
)


def _cpf_teste(base):
    """
    Gera CPF matematicamente válido para fixtures.
    Não representa pessoa real conhecida.
    """

    numeros = [
        int(x)
        for x in base
    ]

    if len(numeros) != 9:
        raise ValueError(
            "A base deve possuir 9 dígitos."
        )

    soma = sum(
        numero * peso
        for numero, peso
        in zip(
            numeros,
            range(10, 1, -1),
        )
    )

    resto = (
        soma * 10
    ) % 11

    primeiro = (
        0
        if resto == 10
        else resto
    )

    numeros.append(
        primeiro
    )

    soma = sum(
        numero * peso
        for numero, peso
        in zip(
            numeros,
            range(11, 1, -1),
        )
    )

    resto = (
        soma * 10
    ) % 11

    segundo = (
        0
        if resto == 10
        else resto
    )

    numeros.append(
        segundo
    )

    return "".join(
        str(x)
        for x in numeros
    )



class JustificativasPontoTests(TestCase):

    def setUp(self):

        self.usuario = (
            User.objects.create_user(
                username="analista_just",
            )
        )

        self.funcionario = (
            Funcionario.objects.create(
                nome="Colaborador Justificativa",
                usuario="colaboradorjust",
                cpf=_cpf_teste("314159265"),
                tipo_vinculo="clt",
                data_admissao=date(
                    2026,
                    1,
                    1,
                ),
            )
        )

        self.folha = (
            FolhaPonto.objects.create(
                funcionario=self.funcionario,
                competencia=date(
                    2026,
                    10,
                    1,
                ),
            )
        )

        self.dia = (
            DiaFolhaPonto.objects.create(
                folha_ponto=self.folha,
                funcionario=self.funcionario,
                data=date(
                    2026,
                    10,
                    5,
                ),
                tipo_dia="trabalho",
                horas_previstas=Decimal(
                    "8.00"
                ),
            )
        )

        self.tipo = (
            TipoJustificativa.objects.create(
                codigo="regra-teste",
                nome="Regra de teste",
                fundamento_tipo="legal",
                fundamento=(
                    "Fundamento normativo de teste."
                ),
                dispositivo="Art. teste",
                fonte="Fonte oficial de teste",
                vigencia_inicio=date(
                    2026,
                    1,
                    1,
                ),
                exige_documento=True,
                documento_sensivel=True,
                permite_abono_parcial=True,
                permite_compensacao=True,
            )
        )

    def criar_regime_banco(self):

        return RegimeBancoHoras.objects.create(
            funcionario=self.funcionario,
            tipo="individual_6m",
            data_inicio=date(
                2026,
                1,
                1,
            ),
            prazo_compensacao_meses=6,
            tratamento_vencimento="pagar",
            fundamento=(
                "Regime de teste."
            ),
            referencia_documento="REG-TESTE",
            ativo=True,
        )

    def criar_solicitacao(
        self,
        *,
        minutos,
        ocorrencia="ausencia_parcial",
    ):

        return criar_justificativa(
            funcionario=self.funcionario,
            dia_folha_ponto=self.dia,
            tipo=self.tipo,
            ocorrencia=ocorrencia,
            motivo="Motivo de teste",
            minutos_solicitados=minutos,
            solicitado_por=self.usuario,
            referencia_documento="DOC-TESTE",
        )

    def decidir(
        self,
        justificativa,
        *,
        decisao,
        abonados=None,
        compensar=0,
    ):

        return registrar_decisao(
            justificativa=justificativa,
            decisao=decisao,
            decidido_por=self.usuario,
            fundamento_tipo="legal",
            fundamento=(
                "Fundamento aplicado ao caso."
            ),
            dispositivo="Art. teste",
            fonte="Fonte oficial de teste",
            motivacao=(
                "Documentação conferida e decisão "
                "motivada para teste."
            ),
            minutos_abonados=abonados,
            minutos_compensar=compensar,
        )

    def test_falta_integral_abonada_libera_dia(self):

        justificativa = (
            self.criar_solicitacao(
                minutos=480,
                ocorrencia="falta_integral",
            )
        )

        self.decidir(
            justificativa,
            decisao="abono_integral",
        )

        resultado = (
            apurar_dia_folha_ponto(
                self.dia,
            )
        )

        self.assertEqual(
            resultado["status"],
            "falta_integral_abonada",
        )

        self.assertEqual(
            resultado[
                "horas_faltas_atrasos"
            ],
            Decimal("0.00"),
        )

        self.assertEqual(
            resultado[
                "saldo_banco_candidato"
            ],
            Decimal("0.00"),
        )

        self.assertEqual(
            resultado[
                "horas_abonadas"
            ],
            Decimal("8.00"),
        )

    def test_abono_parcial_reduz_deficit(self):

        self.dia.entrada_1 = time(
            8,
            0,
        )

        self.dia.saida_1 = time(
            12,
            0,
        )

        self.dia.entrada_2 = time(
            13,
            0,
        )

        self.dia.saida_2 = time(
            15,
            0,
        )

        self.dia.save()

        justificativa = (
            self.criar_solicitacao(
                minutos=120,
            )
        )

        self.decidir(
            justificativa,
            decisao="abono_parcial",
            abonados=60,
        )

        resultado = (
            apurar_dia_folha_ponto(
                self.dia,
            )
        )

        self.assertEqual(
            resultado[
                "horas_faltas_atrasos"
            ],
            Decimal("1.00"),
        )

        self.assertEqual(
            resultado[
                "horas_abonadas"
            ],
            Decimal("1.00"),
        )

        self.assertEqual(
            resultado[
                "saldo_banco_candidato"
            ],
            Decimal("-1.00"),
        )

    def test_indeferimento_nao_abona(self):

        self.dia.entrada_1 = time(
            8,
            0,
        )

        self.dia.saida_1 = time(
            12,
            0,
        )

        self.dia.entrada_2 = time(
            13,
            0,
        )

        self.dia.saida_2 = time(
            15,
            0,
        )

        self.dia.save()

        justificativa = (
            self.criar_solicitacao(
                minutos=120,
            )
        )

        self.decidir(
            justificativa,
            decisao="indeferido",
            abonados=0,
        )

        resultado = (
            apurar_dia_folha_ponto(
                self.dia,
            )
        )

        self.assertEqual(
            resultado[
                "horas_faltas_atrasos"
            ],
            Decimal("2.00"),
        )

        self.assertEqual(
            resultado[
                "horas_abonadas"
            ],
            Decimal("0.00"),
        )

    def test_snapshot_da_regra_e_preservado(self):

        justificativa = (
            self.criar_solicitacao(
                minutos=480,
                ocorrencia="falta_integral",
            )
        )

        decisao = self.decidir(
            justificativa,
            decisao="abono_integral",
        )

        self.assertEqual(
            decisao.snapshot_regra[
                "codigo"
            ],
            "regra-teste",
        )

        self.assertEqual(
            decisao.snapshot_regra[
                "fundamento"
            ],
            (
                "Fundamento normativo "
                "de teste."
            ),
        )

        self.assertTrue(
            decisao.snapshot_regra[
                "documento_sensivel"
            ]
        )

    def test_decisao_nao_pode_superar_solicitado(self):

        justificativa = (
            self.criar_solicitacao(
                minutos=60,
            )
        )

        with self.assertRaises(
            ValidationError
        ):

            self.decidir(
                justificativa,
                decisao="abono_parcial",
                abonados=80,
            )

    def test_funcionario_deve_corresponder_ao_dia(self):

        outro = (
            Funcionario.objects.create(
                nome="Outro Colaborador",
                usuario="outrojust",
                cpf=_cpf_teste("271828182"),
                tipo_vinculo="clt",
                data_admissao=date(
                    2026,
                    1,
                    1,
                ),
            )
        )

        objeto = JustificativaPonto(
            funcionario=outro,
            dia_folha_ponto=self.dia,
            tipo=self.tipo,
            ocorrencia="falta_integral",
            motivo="Teste",
            minutos_solicitados=480,
        )

        with self.assertRaises(
            ValidationError
        ):

            objeto.full_clean()

    def test_nova_decisao_preserva_historico(self):

        justificativa = (
            self.criar_solicitacao(
                minutos=480,
                ocorrencia="falta_integral",
            )
        )

        primeira = self.decidir(
            justificativa,
            decisao="indeferido",
            abonados=0,
        )

        segunda = self.decidir(
            justificativa,
            decisao="abono_integral",
        )

        primeira.refresh_from_db()

        self.assertFalse(
            primeira.ativo
        )

        self.assertTrue(
            segunda.ativo
        )

        self.assertEqual(
            segunda.substitui_id,
            primeira.pk,
        )

        resumo = resumo_decisoes_dia(
            self.dia
        )

        self.assertEqual(
            resumo[
                "minutos_abonados"
            ],
            480,
        )

        self.assertEqual(
            DecisaoJustificativa.objects.filter(
                justificativa=justificativa,
            ).count(),
            2,
        )

    def test_reprocessamento_abono_nao_acumula_horas(self):

        self.dia.entrada_1 = time(
            8,
            0,
        )

        self.dia.saida_1 = time(
            12,
            0,
        )

        self.dia.entrada_2 = time(
            13,
            0,
        )

        self.dia.saida_2 = time(
            15,
            0,
        )

        self.dia.save()

        justificativa = (
            self.criar_solicitacao(
                minutos=120,
            )
        )

        self.decidir(
            justificativa,
            decisao="abono_parcial",
            abonados=60,
        )

        primeiro = (
            apurar_dia_folha_ponto(
                self.dia,
            )
        )

        self.dia.refresh_from_db()

        segundo = (
            apurar_dia_folha_ponto(
                self.dia,
            )
        )

        self.assertEqual(
            primeiro[
                "horas_abonadas"
            ],
            Decimal("1.00"),
        )

        self.assertEqual(
            segundo[
                "horas_abonadas"
            ],
            Decimal("1.00"),
        )

        self.dia.refresh_from_db()

        self.assertEqual(
            self.dia.horas_abonadas,
            Decimal("1.00"),
        )

    def test_compensacao_parcial_movimenta_somente_autorizado(self):

        self.criar_regime_banco()

        self.dia.entrada_1 = time(8, 0)
        self.dia.saida_1 = time(12, 0)
        self.dia.entrada_2 = time(13, 0)
        self.dia.saida_2 = time(15, 0)
        self.dia.save()

        justificativa = (
            self.criar_solicitacao(
                minutos=60,
            )
        )

        self.decidir(
            justificativa,
            decisao="compensacao",
            compensar=60,
        )

        resultado = (
            apurar_dia_folha_ponto(
                self.dia
            )
        )

        self.assertEqual(
            resultado[
                "horas_faltas_atrasos"
            ],
            Decimal("2.00"),
        )

        self.assertEqual(
            resultado[
                "horas_compensacao_autorizada"
            ],
            Decimal("1.00"),
        )

        self.dia.refresh_from_db()

        tratamento = tratar_saldo_dia(
            self.dia
        )

        self.assertEqual(
            tratamento["horas_banco"],
            Decimal("1.00"),
        )

        self.assertEqual(
            tratamento["horas_folha"],
            Decimal("1.00"),
        )

        movimento = (
            MovimentoBancoHoras.objects.get()
        )

        self.assertEqual(
            movimento.tipo,
            "debito",
        )

        self.assertEqual(
            movimento.horas,
            Decimal("1.00"),
        )

        self.dia.refresh_from_db()

        self.assertEqual(
            horas_falta_para_folha_dia(
                self.dia
            ),
            Decimal("1.00"),
        )


    def test_compensacao_integral_falta_sem_marcacoes(self):

        self.criar_regime_banco()

        justificativa = (
            self.criar_solicitacao(
                minutos=480,
                ocorrencia="falta_integral",
            )
        )

        self.decidir(
            justificativa,
            decisao="compensacao",
            compensar=480,
        )

        resultado = (
            apurar_dia_folha_ponto(
                self.dia
            )
        )

        self.assertEqual(
            resultado["status"],
            (
                "falta_integral_"
                "compensacao_autorizada"
            ),
        )

        self.assertEqual(
            resultado[
                "horas_compensacao_autorizada"
            ],
            Decimal("8.00"),
        )

        pendencias = (
            validar_competencia_pronta_para_fechamento(
                self.folha
            )
        )

        datas = [
            item["data"]
            for item in pendencias
        ]

        self.assertNotIn(
            self.dia.data,
            datas,
        )


    def test_compensacao_sem_regime_e_bloqueada(self):

        self.dia.entrada_1 = time(8, 0)
        self.dia.saida_1 = time(12, 0)
        self.dia.entrada_2 = time(13, 0)
        self.dia.saida_2 = time(15, 0)
        self.dia.save()

        justificativa = (
            self.criar_solicitacao(
                minutos=60,
            )
        )

        self.decidir(
            justificativa,
            decisao="compensacao",
            compensar=60,
        )

        apurar_dia_folha_ponto(
            self.dia
        )

        self.dia.refresh_from_db()

        with self.assertRaises(
            ValidationError
        ):

            tratar_saldo_dia(
                self.dia
            )


    def test_compensacao_reprocessada_nao_duplica_movimento(self):

        self.criar_regime_banco()

        self.dia.entrada_1 = time(8, 0)
        self.dia.saida_1 = time(12, 0)
        self.dia.entrada_2 = time(13, 0)
        self.dia.saida_2 = time(15, 0)
        self.dia.save()

        justificativa = (
            self.criar_solicitacao(
                minutos=60,
            )
        )

        self.decidir(
            justificativa,
            decisao="compensacao",
            compensar=60,
        )

        apurar_dia_folha_ponto(
            self.dia
        )

        self.dia.refresh_from_db()

        primeiro = tratar_saldo_dia(
            self.dia
        )

        segundo = tratar_saldo_dia(
            self.dia
        )

        self.assertEqual(
            primeiro["movimento"].pk,
            segundo["movimento"].pk,
        )

        self.assertEqual(
            MovimentoBancoHoras.objects.count(),
            1,
        )


    def test_abono_e_compensacao_preservam_restante_folha(self):

        self.criar_regime_banco()

        self.dia.entrada_1 = time(8, 0)
        self.dia.saida_1 = time(12, 0)
        self.dia.entrada_2 = time(13, 0)
        self.dia.saida_2 = time(14, 0)
        self.dia.save()

        just_abono = (
            self.criar_solicitacao(
                minutos=30,
            )
        )

        self.decidir(
            just_abono,
            decisao="abono_integral",
        )

        just_comp = (
            self.criar_solicitacao(
                minutos=60,
            )
        )

        self.decidir(
            just_comp,
            decisao="compensacao",
            compensar=60,
        )

        resultado = (
            apurar_dia_folha_ponto(
                self.dia
            )
        )

        self.assertEqual(
            resultado[
                "horas_abonadas"
            ],
            Decimal("0.50"),
        )

        self.assertEqual(
            resultado[
                "horas_faltas_atrasos"
            ],
            Decimal("2.50"),
        )

        self.assertEqual(
            resultado[
                "horas_compensacao_autorizada"
            ],
            Decimal("1.00"),
        )

        self.dia.refresh_from_db()

        tratar_saldo_dia(
            self.dia
        )

        self.dia.refresh_from_db()

        self.assertEqual(
            horas_falta_para_folha_dia(
                self.dia
            ),
            Decimal("1.50"),
        )
