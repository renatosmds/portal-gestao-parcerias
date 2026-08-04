from datetime import date, timedelta
from decimal import Decimal
import os

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.analise.models import Analise
from apps.conciliacao.models import Conciliacao, Movimentacao, VinculoConciliacao
from apps.diligencias.models import Diligencia, RespostaDiligencia
from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.fornecedores.models import Fornecedores
from apps.lancamentos.models import Lancamento
from apps.metas.models import MetaExecucao
from apps.parcerias.models import Parcerias
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos
from apps.transparencia.models import PublicacaoDocumento, PublicacaoParceria


RUBRICAS = (
    ("RH", "Recursos humanos", Decimal("3200.00")),
    ("ENC", "Encargos sociais", Decimal("1180.00")),
    ("MAT", "Material de consumo", Decimal("760.00")),
    ("ALIM", "Gêneros alimentícios", Decimal("940.00")),
    ("SPJ", "Serviços de terceiros — pessoa jurídica", Decimal("1450.00")),
    ("SPF", "Serviços de terceiros — pessoa física", Decimal("980.00")),
    ("LOC", "Locação de bens e equipamentos", Decimal("1250.00")),
    ("TRAN", "Transporte e deslocamento", Decimal("620.00")),
    ("COM", "Comunicação e divulgação", Decimal("530.00")),
    ("TRIB", "Tributos e taxas", Decimal("410.00")),
    ("OUT", "Outras despesas previstas", Decimal("350.00")),
)

CENARIOS = (
    {
        "municipio": "Prefeitura Municipal de Vale Sereno — Demonstração",
        "osc": "Instituto Caminhos de Vale Sereno — Demonstração",
        "cnpj": "10.000.001/0001-01",
        "termo": "001/2026",
        "objeto": "Atendimento socioassistencial a famílias em situação de vulnerabilidade.",
        "situacao": Prestacao.SituacaoWorkflow.APROVADA,
        "analise_status": "Aprovada",
        "publicada": True,
    },
    {
        "municipio": "Prefeitura Municipal de Nova Esperança — Demonstração",
        "osc": "Associação Rede Cidadã de Nova Esperança — Demonstração",
        "cnpj": "20.000.002/0001-02",
        "termo": "002/2026",
        "objeto": "Oficinas de inclusão produtiva e fortalecimento de vínculos.",
        "situacao": Prestacao.SituacaoWorkflow.APROVADA_RESSALVAS,
        "analise_status": "Aprovada com ressalvas",
        "publicada": True,
    },
    {
        "municipio": "Prefeitura Municipal de Jardim das Águas — Demonstração",
        "osc": "Fundação Sementes de Jardim das Águas — Demonstração",
        "cnpj": "30.000.003/0001-03",
        "termo": "003/2026",
        "objeto": "Ações de proteção social, convivência e atendimento comunitário.",
        "situacao": Prestacao.SituacaoWorkflow.REPROVADA,
        "analise_status": "Reprovada com glosa parcial",
        "publicada": True,
    },
)


class Command(BaseCommand):
    help = (
        "Cria três ciclos demonstrativos completos, com três prefeituras, "
        "três OSCs e três lançamentos para cada rubrica."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        usuario = self._obter_administrador()
        totais = {
            "municipios": 0,
            "oscs": 0,
            "termos": 0,
            "prestacoes": 0,
            "lancamentos": 0,
            "documentos": 0,
            "movimentacoes": 0,
            "metas": 0,
            "diligencias": 0,
        }

        for indice, dados in enumerate(CENARIOS, start=1):
            resultado = self._criar_ciclo(indice, dados, usuario)
            for chave, quantidade in resultado.items():
                totais[chave] += quantidade

        self.stdout.write(self.style.SUCCESS(
            "Base demonstrativa do ciclo completo preparada com sucesso."
        ))
        self.stdout.write(
            "Resumo: "
            f"{totais['municipios']} prefeituras; "
            f"{totais['oscs']} OSCs; "
            f"{totais['termos']} Termos; "
            f"{totais['prestacoes']} prestações; "
            f"{totais['lancamentos']} lançamentos; "
            f"{totais['documentos']} documentos; "
            f"{totais['movimentacoes']} movimentações; "
            f"{totais['metas']} metas; "
            f"{totais['diligencias']} diligências."
        )
        self.stdout.write(
            self.style.WARNING(
                "Todos os registros possuem nomes, documentos e valores fictícios."
            )
        )

    def _obter_administrador(self):
        User = get_user_model()
        username = os.getenv("DEMO_ADMIN_USERNAME", "demo_admin")
        password = os.getenv("DEMO_ADMIN_PASSWORD", "")
        usuario, _ = User.objects.get_or_create(
            username=username,
            defaults={
                "email": "demo@exemplo.invalid",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        alterado = False
        if not usuario.is_staff or not usuario.is_superuser:
            usuario.is_staff = True
            usuario.is_superuser = True
            alterado = True
        if password:
            usuario.set_password(password)
            alterado = True
        if alterado:
            usuario.save()
        return usuario

    def _criar_ciclo(self, indice, dados, usuario):
        inicio = date(2026, 1, 1)
        fim = date(2026, 12, 31)
        valor_global = Decimal("360000.00") + Decimal(indice * 30000)

        prefeitura, criada_prefeitura = Empresa.objects.get_or_create(
            nome=dados["municipio"]
        )

        termo, criado_termo = Termos.objects.get_or_create(
            empresa=prefeitura,
            numtermo=dados["termo"],
            defaults={
                "nomeosc": dados["osc"][:50],
                "termo": f"Termo de Colaboração nº {dados['termo']}",
                "tipo": "Termo de Colaboração",
                "objeto": dados["objeto"],
                "vigencia": "01/01/2026 a 31/12/2026",
                "inicioVigencia": "01/01/2026",
                "terminoVigencia": "31/12/2026",
                "assinatura": inicio,
                "valorglobal": valor_global,
                "valorrepasse": valor_global,
                "valorsaldo": Decimal("0.00"),
                "status": "Encerrado para demonstração",
                "nomemunicipio": dados["municipio"][:50],
                "nomerepresentante": f"Representante fictício da OSC {indice}",
                "observacoes": "Registro criado exclusivamente para demonstração.",
            },
        )

        prestacao, criada_prestacao = Prestacao.objects.get_or_create(
            empresa=prefeitura,
            numtermo=dados["termo"],
            defaults={
                "tipo": "cnpj",
                "tipoTermo": "TC",
                "credor": dados["osc"],
                "CpfCnpj": dados["cnpj"],
                "valorContrato": float(valor_global),
                "qtdParcelas": "12",
                "situacao_workflow": dados["situacao"],
                "concluida": dados["situacao"] in {
                    Prestacao.SituacaoWorkflow.APROVADA,
                    Prestacao.SituacaoWorkflow.APROVADA_RESSALVAS,
                    Prestacao.SituacaoWorkflow.REPROVADA,
                    Prestacao.SituacaoWorkflow.ENCERRADA,
                },
                "analista_responsavel": usuario,
                "enviada_em": timezone.now() - timedelta(days=45),
                "recebida_em": timezone.now() - timedelta(days=43),
            },
        )

        parceria, criada_parceria = Parcerias.objects.get_or_create(
            empresa=prefeitura,
            numtermo=termo,
            defaults={
                "nomeOSC": dados["osc"],
                "status": dados["analise_status"],
                "historico": (
                    "Formalização, execução, prestação de contas, conferência, "
                    "conciliação, análise e decisão demonstrativas."
                ),
                "concluido": True,
            },
        )

        if prefeitura.termos_id is None or prefeitura.prestacao_id is None:
            prefeitura.termos = prefeitura.termos or termo
            prefeitura.prestacao = prefeitura.prestacao or prestacao
            prefeitura.parcerias = prefeitura.parcerias or parceria
            prefeitura.save(update_fields=["termos", "prestacao", "parcerias"])

        analise, _ = Analise.objects.get_or_create(
            empresa=prefeitura,
            numtermo=termo,
            prestacao=prestacao,
            numRA=f"RA-{indice:02d}/2026",
            defaults={
                "nomeOSC": dados["osc"],
                "item": "Ciclo completo",
                "status": dados["analise_status"],
                "concluida": True,
                "inconformidade": (
                    "Sem inconformidade relevante."
                    if indice == 1
                    else "Pendência demonstrativa identificada durante a análise."
                ),
                "recomendacoes": (
                    "Manter a organização documental e a conciliação mensal."
                ),
                "posicaoSecretaria": dados["analise_status"],
            },
        )

        conciliacao, _ = Conciliacao.objects.get_or_create(
            prestacao=prestacao,
            defaults={
                "saldo_inicial": Decimal("0.00"),
                "observacoes": "Conciliação bancária fictícia do ciclo completo.",
                "criado_por": usuario,
            },
        )

        repasse, criada_repasse = Movimentacao.objects.get_or_create(
            conciliacao=conciliacao,
            data=inicio + timedelta(days=4),
            descricao=f"Repasse municipal — {dados['termo']}",
            valor=valor_global,
            tipo=Movimentacao.Tipo.CREDITO,
            defaults={
                "categoria": Movimentacao.Categoria.REPASSE,
                "documento": f"REP-{indice:02d}-2026",
                "favorecido": dados["osc"],
                "situacao": Movimentacao.Situacao.CONCILIADA,
                "saldo_apos": valor_global,
            },
        )

        total_despesas = Decimal("0.00")
        qtd_lancamentos = 0
        qtd_documentos = 0
        qtd_movimentacoes = 1 if criada_repasse else 0
        primeiro_com_pendencia = None

        for rubrica_indice, (codigo, rubrica, valor_base) in enumerate(RUBRICAS, start=1):
            fornecedor, _ = Fornecedores.objects.get_or_create(
                empresa=prefeitura,
                numero=f"{indice}{rubrica_indice:02d}000000001",
                defaults={
                    "credor": f"Fornecedor {rubrica} — Município {indice}",
                    "razao": f"Fornecedor Demonstrativo {codigo} Ltda.",
                    "fantasia": f"Demo {codigo}",
                    "pessoa": "jurídica",
                    "tipo": "cnpj",
                    "cidade": dados["municipio"].replace(
                        "Prefeitura Municipal de ", ""
                    ).replace(" — Demonstração", ""),
                    "estado": "MG",
                    "email": f"fornecedor.{indice}.{codigo.lower()}@exemplo.invalid",
                },
            )

            for repeticao in range(1, 4):
                sequencial = (rubrica_indice - 1) * 3 + repeticao
                data_documento = inicio + timedelta(days=10 + sequencial * 5)
                valor = valor_base + Decimal(indice * 25 + repeticao * 10)
                numero = f"{indice:02d}-{codigo}-{repeticao:02d}"

                situacao = Lancamento.Situacao.REGULAR
                tipo_glosa = Lancamento.TipoGlosa.NENHUMA
                valor_glosa = Decimal("0.00")
                motivo_glosa = ""
                justificativa = "Documento e pagamento conferidos."
                recomendacao = "Manter documentação organizada."

                if indice == 2 and codigo == "COM" and repeticao == 3:
                    situacao = Lancamento.Situacao.RESSALVA
                    justificativa = (
                        "Documento apresentado após diligência, sem prejuízo financeiro."
                    )
                    primeiro_com_pendencia = primeiro_com_pendencia or numero

                if indice == 3 and codigo == "OUT" and repeticao == 3:
                    situacao = Lancamento.Situacao.GLOSADO
                    tipo_glosa = Lancamento.TipoGlosa.PARCIAL
                    valor_glosa = (valor * Decimal("0.40")).quantize(Decimal("0.01"))
                    motivo_glosa = Lancamento.MotivoGlosa.SEM_COMPROVACAO
                    justificativa = "Comprovação parcial para fins demonstrativos."
                    recomendacao = "Restituir o valor glosado e reforçar os controles."
                    primeiro_com_pendencia = primeiro_com_pendencia or numero

                lancamento, criado_lancamento = Lancamento.objects.get_or_create(
                    empresa=prefeitura,
                    numero_lancamento=numero,
                    defaults={
                        "termo": termo,
                        "prestacao": prestacao,
                        "fornecedor": fornecedor,
                        "analise": analise,
                        "criado_por": usuario,
                        "tipo_documento": Lancamento.TipoDocumento.NFE,
                        "numero_documento": f"NF-{numero}",
                        "data_documento": data_documento,
                        "data_pagamento": data_documento + timedelta(days=2),
                        "descricao": f"{rubrica} — parcela demonstrativa {repeticao}",
                        "valor_documento": valor,
                        "valor_glosa": valor_glosa,
                        "tipo_glosa": tipo_glosa,
                        "motivo_glosa": motivo_glosa,
                        "fundamentacao_glosa": (
                            "Glosa parcial fictícia para demonstrar o ciclo completo."
                            if valor_glosa
                            else ""
                        ),
                        "situacao": situacao,
                        "atestado": situacao != Lancamento.Situacao.GLOSADO,
                        "justificativa": justificativa,
                        "recomendacao": recomendacao,
                    },
                )
                if criado_lancamento:
                    qtd_lancamentos += 1

                total_despesas += lancamento.valor_documento

                movimento, criado_movimento = Movimentacao.objects.get_or_create(
                    conciliacao=conciliacao,
                    data=lancamento.data_pagamento,
                    descricao=f"Pagamento {lancamento.numero_lancamento}",
                    valor=lancamento.valor_documento,
                    tipo=Movimentacao.Tipo.DEBITO,
                    defaults={
                        "categoria": Movimentacao.Categoria.PAGAMENTO,
                        "documento": lancamento.numero_documento,
                        "favorecido": str(fornecedor),
                        "situacao": Movimentacao.Situacao.PENDENTE,
                    },
                )
                if criado_movimento:
                    qtd_movimentacoes += 1

                VinculoConciliacao.objects.get_or_create(
                    movimentacao=movimento,
                    lancamento=lancamento,
                    defaults={
                        "valor": lancamento.valor_documento,
                        "observacao": "Vínculo demonstrativo confirmado.",
                        "confirmado_por": usuario,
                    },
                )

                documento, criado_documento = Documento.objects.get_or_create(
                    lancamento=lancamento,
                    tipo=Documento.Tipo.NOTA_FISCAL,
                    defaults={
                        "descricao": f"Nota fiscal fictícia — {rubrica}",
                        "empresa": prefeitura,
                        "termo": termo,
                        "prestacao": prestacao,
                        "conferido_por": usuario,
                        "status": (
                            Documento.Status.COM_PENDENCIA
                            if situacao == Lancamento.Situacao.GLOSADO
                            else Documento.Status.CONFERIDO
                        ),
                        "numero_documento": lancamento.numero_documento,
                        "data_documento": lancamento.data_documento,
                        "documento_legivel": True,
                        "dados_compativeis": True,
                        "vigencia_valida": True,
                        "pagamento_comprovado": True,
                        "atesto_valido": situacao != Lancamento.Situacao.GLOSADO,
                        "observacoes": "Arquivo textual fictício para demonstração.",
                    },
                )
                if criado_documento:
                    documento.arquivo.save(
                        f"documento_{numero}.txt",
                        ContentFile(
                            (
                                "DOCUMENTO EXCLUSIVAMENTE FICTÍCIO\n"
                                f"OSC: {dados['osc']}\n"
                                f"Rubrica: {rubrica}\n"
                                f"Valor: R$ {valor}\n"
                            ).encode("utf-8")
                        ),
                        save=True,
                    )
                    qtd_documentos += 1

                PublicacaoDocumento.objects.get_or_create(
                    documento=documento,
                    defaults={
                        "classificacao": PublicacaoDocumento.Classificacao.PUBLICO,
                        "publicado": dados["publicada"],
                        "titulo_publico": f"Documento demonstrativo — {rubrica}",
                        "descricao_publica": (
                            "Documento fictício, sem dados pessoais ou bancários reais."
                        ),
                        "publicado_em": timezone.now() if dados["publicada"] else None,
                        "publicado_por": usuario if dados["publicada"] else None,
                    },
                )

        saldo_final = valor_global - total_despesas
        conciliacao.saldo_final_informado = saldo_final
        conciliacao.save(update_fields=["saldo_final_informado", "atualizado_em"])
        conciliacao.recalcular_situacao()

        for meta_indice in range(1, 4):
            previsto = Decimal(100 * meta_indice)
            if indice == 1:
                realizado = previsto
                situacao_meta = MetaExecucao.Situacao.ATINGIDA
            elif indice == 2:
                realizado = previsto * Decimal("0.90")
                situacao_meta = MetaExecucao.Situacao.PARCIAL
            else:
                realizado = previsto * Decimal("0.65")
                situacao_meta = MetaExecucao.Situacao.NAO_ATINGIDA

            MetaExecucao.objects.get_or_create(
                prestacao=prestacao,
                codigo=f"M{indice}.{meta_indice}",
                defaults={
                    "titulo": f"Meta demonstrativa {meta_indice}",
                    "descricao": dados["objeto"],
                    "unidade": MetaExecucao.Unidade.PESSOAS,
                    "valor_previsto": previsto,
                    "valor_realizado": realizado,
                    "inicio": inicio,
                    "fim": fim,
                    "situacao": situacao_meta,
                    "justificativa": (
                        "Resultado fictício utilizado para demonstrar o acompanhamento."
                    ),
                    "responsavel": f"Coordenador fictício {indice}",
                    "criado_por": usuario,
                    "atualizado_por": usuario,
                },
            )

        qtd_diligencias = 0
        if indice in (2, 3):
            lancamento_pendente = Lancamento.objects.filter(
                empresa=prefeitura,
                numero_lancamento=primeiro_com_pendencia,
            ).first()
            diligencia, criada_diligencia = Diligencia.objects.get_or_create(
                empresa=prefeitura,
                prestacao=prestacao,
                assunto=f"Diligência demonstrativa — {dados['termo']}",
                defaults={
                    "descricao": (
                        "Apresentar esclarecimentos e documentação complementar."
                    ),
                    "fundamento": "Procedimento fictício para treinamento.",
                    "prioridade": Diligencia.Prioridade.NORMAL,
                    "status": (
                        Diligencia.Status.ATENDIDA
                        if indice == 2
                        else Diligencia.Status.NAO_ATENDIDA
                    ),
                    "prazo_resposta": timezone.localdate() + timedelta(days=10),
                    "lancamento": lancamento_pendente,
                    "responsavel": usuario,
                    "criada_por": usuario,
                    "enviada_em": timezone.now() - timedelta(days=15),
                    "visualizada_em": timezone.now() - timedelta(days=14),
                    "encerrada_em": timezone.now() - timedelta(days=5),
                },
            )
            if criada_diligencia:
                qtd_diligencias += 1
            RespostaDiligencia.objects.get_or_create(
                diligencia=diligencia,
                criada_por=usuario,
                defaults={
                    "texto": (
                        "Resposta fictícia apresentada com esclarecimentos."
                        if indice == 2
                        else "Resposta fictícia insuficiente para sanar a pendência."
                    )
                },
            )

        PublicacaoParceria.objects.get_or_create(
            termo=termo,
            defaults={
                "publicada": dados["publicada"],
                "orgao_responsavel": dados["municipio"],
                "resumo_publico": (
                    f"{dados['osc']} — {dados['objeto']} "
                    "Todos os dados são exclusivamente fictícios."
                ),
                "publicada_em": timezone.now() if dados["publicada"] else None,
                "publicada_por": usuario if dados["publicada"] else None,
            },
        )

        termo.totalDeLacamentos = str(len(RUBRICAS) * 3)
        termo.lacamentosRegulares = str(
            Lancamento.objects.filter(
                empresa=prefeitura,
                situacao=Lancamento.Situacao.REGULAR,
            ).count()
        )
        termo.lacamentosIrregulares = str(
            Lancamento.objects.filter(
                empresa=prefeitura,
                situacao__in=[
                    Lancamento.Situacao.RESSALVA,
                    Lancamento.Situacao.REPROVADO,
                ],
            ).count()
        )
        termo.lacamentosGlosados = str(
            Lancamento.objects.filter(
                empresa=prefeitura,
                situacao=Lancamento.Situacao.GLOSADO,
            ).count()
        )
        termo.valoresGlosados = str(
            sum(
                Lancamento.objects.filter(empresa=prefeitura)
                .values_list("valor_glosa", flat=True),
                Decimal("0.00"),
            )
        )
        termo.saldoFinal = str(saldo_final)
        termo.save(
            update_fields=[
                "totalDeLacamentos",
                "lacamentosRegulares",
                "lacamentosIrregulares",
                "lacamentosGlosados",
                "valoresGlosados",
                "saldoFinal",
            ]
        )

        return {
            "municipios": 1 if criada_prefeitura else 0,
            "oscs": 1 if criada_parceria else 0,
            "termos": 1 if criado_termo else 0,
            "prestacoes": 1 if criada_prestacao else 0,
            "lancamentos": qtd_lancamentos,
            "documentos": qtd_documentos,
            "movimentacoes": qtd_movimentacoes,
            "metas": 3,
            "diligencias": qtd_diligencias,
        }
