from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.analise.models import Analise
from apps.conciliacao.models import (
    Conciliacao,
    Movimentacao,
    VinculoConciliacao,
)
from apps.diligencias.models import (
    Diligencia,
    RespostaDiligencia,
)
from apps.documentos.models import Documento
from apps.empresas.models import Empresa
from apps.fornecedores.models import Fornecedores
from apps.lancamentos.models import Lancamento
from apps.metas.models import MetaExecucao
from apps.parcerias.models import Parcerias
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos


class Command(BaseCommand):
    help = (
        "Cria uma base demonstrativa enxuta do PGP com "
        "casos funcionais selecionados."
    )

    def handle(self, *args, **options):
        usuario = self._obter_usuario()
        empresa, termo, prestacao, analise, conciliacao = (
            self._estrutura_base(usuario)
        )

        casos = self._casos()

        for indice, caso in enumerate(casos, start=1):
            self.stdout.write(
                f"[{indice}/{len(casos)}] {caso['codigo']} - "
                f"{caso['titulo']}"
            )

            self._criar_lancamento(
                indice=indice,
                caso=caso,
                usuario=usuario,
                empresa=empresa,
                termo=termo,
                prestacao=prestacao,
                analise=analise,
                conciliacao=conciliacao,
            )

        self._criar_meta(prestacao, usuario)
        self._criar_diligencia(
            empresa=empresa,
            prestacao=prestacao,
            usuario=usuario,
        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Base demonstrativa enxuta criada/atualizada com sucesso."
            )
        )
        self.stdout.write(
            "OSC: Instituto PGP Demonstrativo"
        )
        self.stdout.write(
            "Termo: D001/2026"
        )
        self.stdout.write(
            "Lancamentos funcionais: 8"
        )

    def _obter_usuario(self):
        User = get_user_model()

        usuario = (
            User.objects.filter(is_superuser=True)
            .order_by("id")
            .first()
        )

        if usuario is None:
            raise RuntimeError(
                "Nenhum superusuario encontrado. "
                "Crie um antes de executar este comando."
            )

        return usuario

    def _estrutura_base(self, usuario):
        empresa, _ = Empresa.objects.get_or_create(
            nome="Instituto PGP Demonstrativo"
        )

        termo, _ = Termos.objects.get_or_create(
            empresa=empresa,
            numtermo="D001/2026",
            defaults={
                "nomeosc": "Instituto PGP Demonstrativo",
                "termo": "Termo de Colaboracao D001/2026",
                "tipo": "Termo de Colaboracao",
                "objeto": (
                    "Base demonstrativa funcional para homologacao "
                    "das principais rotinas do PGP."
                ),
                "vigencia": "01/01/2026 a 31/12/2026",
                "inicioVigencia": "01/01/2026",
                "terminoVigencia": "31/12/2026",
                "assinatura": date(2026, 1, 1),
                "valorglobal": Decimal("100000.00"),
                "valorrepasse": Decimal("100000.00"),
                "valorsaldo": Decimal("23500.00"),
                "status": "Em demonstracao",
                "nomemunicipio": "Municipio Demonstrativo",
                "nomerepresentante": "Representante Demonstrativo",
                "observacoes": (
                    "Registro ficticio criado para demonstracao "
                    "funcional do PGP."
                ),
            },
        )

        prestacao, _ = Prestacao.objects.get_or_create(
            empresa=empresa,
            numtermo="D001/2026",
            defaults={
                "tipo": "cnpj",
                "tipoTermo": "TC",
                "credor": "Instituto PGP Demonstrativo",
                "CpfCnpj": "99.999.999/0001-99",
                "valorContrato": 100000.00,
                "qtdParcelas": "12",
                "situacao_workflow": (
                    Prestacao.SituacaoWorkflow.DILIGENCIA
                ),
                "concluida": False,
                "analista_responsavel": usuario,
                "enviada_em": timezone.now() - timedelta(days=30),
                "recebida_em": timezone.now() - timedelta(days=28),
            },
        )

        parceria, _ = Parcerias.objects.get_or_create(
            empresa=empresa,
            numtermo=termo,
            defaults={
                "nomeOSC": "Instituto PGP Demonstrativo",
                "status": "Em analise",
                "historico": (
                    "Parceria ficticia criada para demonstrar "
                    "os principais fluxos do PGP."
                ),
                "concluido": False,
            },
        )

        if empresa.termos_id is None:
            empresa.termos = termo
        if empresa.prestacao_id is None:
            empresa.prestacao = prestacao
        if empresa.parcerias_id is None:
            empresa.parcerias = parceria

        empresa.save()

        analise, _ = Analise.objects.get_or_create(
            empresa=empresa,
            numtermo=termo,
            prestacao=prestacao,
            numRA="RA-DEMO/2026",
            defaults={
                "nomeOSC": "Instituto PGP Demonstrativo",
                "item": "Demonstracao funcional",
                "status": "Em analise",
                "concluida": False,
                "inconformidade": (
                    "Base contem casos regulares, ressalvas, "
                    "glosas e diligencia."
                ),
                "recomendacoes": (
                    "Utilizar os casos para homologacao e treinamento."
                ),
                "posicaoSecretaria": "Em analise",
            },
        )

        conciliacao, _ = Conciliacao.objects.get_or_create(
            prestacao=prestacao,
            defaults={
                "saldo_inicial": Decimal("100000.00"),
                "observacoes": (
                    "Conciliacao ficticia da demo enxuta."
                ),
                "criado_por": usuario,
            },
        )

        return empresa, termo, prestacao, analise, conciliacao

    def _casos(self):
        return (
            {
                "codigo": "DEMO-01",
                "titulo": "Despesa regular",
                "valor": Decimal("12000.00"),
                "situacao": Lancamento.Situacao.REGULAR,
                "glosa": Decimal("0.00"),
                "tipo_glosa": Lancamento.TipoGlosa.NENHUMA,
                "motivo_glosa": "",
                "descricao": (
                    "Despesa regular com documentacao e pagamento "
                    "compativeis."
                ),
                "status_documento": Documento.Status.CONFERIDO,
            },
            {
                "codigo": "DEMO-02",
                "titulo": "Despesa regular - outro fornecedor",
                "valor": Decimal("9000.00"),
                "situacao": Lancamento.Situacao.REGULAR,
                "glosa": Decimal("0.00"),
                "tipo_glosa": Lancamento.TipoGlosa.NENHUMA,
                "motivo_glosa": "",
                "descricao": (
                    "Segundo caso regular para comparacao."
                ),
                "status_documento": Documento.Status.CONFERIDO,
            },
            {
                "codigo": "DEMO-03",
                "titulo": "Aprovacao com ressalva",
                "valor": Decimal("8500.00"),
                "situacao": Lancamento.Situacao.RESSALVA,
                "glosa": Decimal("0.00"),
                "tipo_glosa": Lancamento.TipoGlosa.NENHUMA,
                "motivo_glosa": "",
                "descricao": (
                    "Inconsistencia formal sem prejuizo financeiro."
                ),
                "status_documento": Documento.Status.CONFERIDO,
            },
            {
                "codigo": "DEMO-04",
                "titulo": "Glosa parcial",
                "valor": Decimal("15000.00"),
                "situacao": Lancamento.Situacao.GLOSADO,
                "glosa": Decimal("3000.00"),
                "tipo_glosa": Lancamento.TipoGlosa.PARCIAL,
                "motivo_glosa": Lancamento.MotivoGlosa.SEM_COMPROVACAO,
                "descricao": (
                    "Comprovacao parcial da despesa."
                ),
                "status_documento": Documento.Status.COM_PENDENCIA,
            },
            {
                "codigo": "DEMO-05",
                "titulo": "Glosa integral",
                "valor": Decimal("7000.00"),
                "situacao": Lancamento.Situacao.GLOSADO,
                "glosa": Decimal("7000.00"),
                "tipo_glosa": Lancamento.TipoGlosa.GLOBAL,
                "motivo_glosa": Lancamento.MotivoGlosa.SEM_COMPROVACAO,
                "descricao": (
                    "Despesa sem comprovacao suficiente."
                ),
                "status_documento": Documento.Status.COM_PENDENCIA,
            },
            {
                "codigo": "DEMO-06",
                "titulo": "Pendencia documental",
                "valor": Decimal("6500.00"),
                "situacao": Lancamento.Situacao.RESSALVA,
                "glosa": Decimal("0.00"),
                "tipo_glosa": Lancamento.TipoGlosa.NENHUMA,
                "motivo_glosa": "",
                "descricao": (
                    "Documento apresentado com pendencia formal."
                ),
                "status_documento": Documento.Status.COM_PENDENCIA,
            },
            {
                "codigo": "DEMO-07",
                "titulo": "Pagamento conciliado",
                "valor": Decimal("11000.00"),
                "situacao": Lancamento.Situacao.REGULAR,
                "glosa": Decimal("0.00"),
                "tipo_glosa": Lancamento.TipoGlosa.NENHUMA,
                "motivo_glosa": "",
                "descricao": (
                    "Pagamento regular utilizado para demonstrar "
                    "conciliacao."
                ),
                "status_documento": Documento.Status.CONFERIDO,
            },
            {
                "codigo": "DEMO-08",
                "titulo": "Caso para diligencia",
                "valor": Decimal("7500.00"),
                "situacao": Lancamento.Situacao.RESSALVA,
                "glosa": Decimal("0.00"),
                "tipo_glosa": Lancamento.TipoGlosa.NENHUMA,
                "motivo_glosa": "",
                "descricao": (
                    "Pendencia que exige esclarecimento da OSC."
                ),
                "status_documento": Documento.Status.COM_PENDENCIA,
            },
        )

    def _criar_lancamento(
        self,
        indice,
        caso,
        usuario,
        empresa,
        termo,
        prestacao,
        analise,
        conciliacao,
    ):
        fornecedor, _ = Fornecedores.objects.get_or_create(
            empresa=empresa,
            numero=f"99999999000{indice}",
            defaults={
                "credor": f"Fornecedor Demo {indice}",
                "razao": f"Fornecedor Demonstrativo {indice} Ltda.",
                "fantasia": f"Demo {indice}",
                "pessoa": "juridica",
                "tipo": "cnpj",
                "cidade": "Contagem",
                "estado": "MG",
                "email": f"demo{indice}@exemplo.invalid",
            },
        )

        data_documento = date(2026, 2, 1) + timedelta(
            days=indice * 5
        )

        lancamento, _ = Lancamento.objects.update_or_create(
            empresa=empresa,
            numero_lancamento=caso["codigo"],
            defaults={
                "termo": termo,
                "prestacao": prestacao,
                "fornecedor": fornecedor,
                "analise": analise,
                "criado_por": usuario,
                "tipo_documento": Lancamento.TipoDocumento.NFE,
                "numero_documento": f"NF-{caso['codigo']}",
                "data_documento": data_documento,
                "data_pagamento": data_documento + timedelta(days=2),
                "descricao": caso["descricao"],
                "valor_documento": caso["valor"],
                "valor_glosa": caso["glosa"],
                "tipo_glosa": caso["tipo_glosa"],
                "motivo_glosa": caso["motivo_glosa"],
                "fundamentacao_glosa": (
                    "Caso ficticio para demonstracao de glosa."
                    if caso["glosa"]
                    else ""
                ),
                "situacao": caso["situacao"],
                "atestado": (
                    caso["situacao"]
                    != Lancamento.Situacao.GLOSADO
                ),
                "justificativa": caso["descricao"],
                "recomendacao": (
                    "Regularizar a pendencia quando aplicavel."
                ),
            },
        )

        movimento, _ = Movimentacao.objects.update_or_create(
            conciliacao=conciliacao,
            data=lancamento.data_pagamento,
            descricao=f"Pagamento {caso['codigo']}",
            tipo=Movimentacao.Tipo.DEBITO,
            defaults={
                "valor": lancamento.valor_documento,
                "categoria": Movimentacao.Categoria.PAGAMENTO,
                "documento": lancamento.numero_documento,
                "favorecido": str(fornecedor),
                "situacao": (
                    Movimentacao.Situacao.CONCILIADA
                    if caso["codigo"] == "DEMO-07"
                    else Movimentacao.Situacao.PENDENTE
                ),
            },
        )

        VinculoConciliacao.objects.update_or_create(
            movimentacao=movimento,
            lancamento=lancamento,
            defaults={
                "valor": lancamento.valor_documento,
                "observacao": (
                    "Vinculo ficticio da demonstracao enxuta."
                ),
                "confirmado_por": usuario,
            },
        )

        Documento.objects.update_or_create(
            lancamento=lancamento,
            tipo=Documento.Tipo.NOTA_FISCAL,
            defaults={
                "descricao": (
                    f"Documento ficticio - {caso['titulo']}"
                ),
                "empresa": empresa,
                "termo": termo,
                "prestacao": prestacao,
                "conferido_por": usuario,
                "status": caso["status_documento"],
                "numero_documento": lancamento.numero_documento,
                "data_documento": lancamento.data_documento,
                "documento_legivel": True,
                "dados_compativeis": (
                    caso["status_documento"]
                    == Documento.Status.CONFERIDO
                ),
                "vigencia_valida": True,
                "pagamento_comprovado": True,
                "atesto_valido": (
                    caso["situacao"]
                    != Lancamento.Situacao.GLOSADO
                ),
                "observacoes": (
                    "Documento exclusivamente ficticio."
                ),
            },
        )

    def _criar_meta(self, prestacao, usuario):
        MetaExecucao.objects.update_or_create(
            prestacao=prestacao,
            codigo="DEMO-META-01",
            defaults={
                "titulo": "Meta demonstrativa nao atingida",
                "descricao": (
                    "Demonstrar acompanhamento fisico de meta."
                ),
                "unidade": MetaExecucao.Unidade.PESSOAS,
                "valor_previsto": Decimal("100.00"),
                "valor_realizado": Decimal("65.00"),
                "inicio": date(2026, 1, 1),
                "fim": date(2026, 12, 31),
                "situacao": MetaExecucao.Situacao.NAO_ATINGIDA,
                "justificativa": (
                    "Resultado ficticio para demonstracao."
                ),
                "responsavel": "Coordenador Demonstrativo",
                "criado_por": usuario,
                "atualizado_por": usuario,
            },
        )

    def _criar_diligencia(
        self,
        empresa,
        prestacao,
        usuario,
    ):
        lancamento = Lancamento.objects.filter(
            empresa=empresa,
            numero_lancamento="DEMO-08",
        ).first()

        diligencia, _ = Diligencia.objects.update_or_create(
            empresa=empresa,
            prestacao=prestacao,
            assunto="Diligencia DEMO-08",
            defaults={
                "descricao": (
                    "Apresentar documento complementar e "
                    "esclarecimentos sobre a despesa."
                ),
                "fundamento": (
                    "Caso ficticio para treinamento no PGP."
                ),
                "prioridade": Diligencia.Prioridade.ALTA,
                "status": Diligencia.Status.EM_RESPOSTA,
                "prazo_resposta": (
                    timezone.localdate() + timedelta(days=5)
                ),
                "lancamento": lancamento,
                "responsavel": usuario,
                "criada_por": usuario,
                "enviada_em": (
                    timezone.now() - timedelta(days=2)
                ),
                "visualizada_em": (
                    timezone.now() - timedelta(days=1)
                ),
                "encerrada_em": None,
            },
        )

        RespostaDiligencia.objects.get_or_create(
            diligencia=diligencia,
            criada_por=usuario,
            defaults={
                "texto": (
                    "Resposta ficticia ainda insuficiente para "
                    "sanar integralmente a pendencia."
                )
            },
        )
