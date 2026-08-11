"""Serviços do dashboard integrado do Portal de Gestão de Parcerias.

A Sprint 15 mantém os modelos existentes e consolida os dados em uma única
camada de leitura. Nenhuma migração é necessária.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Iterable

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.dateparse import parse_date

from apps.analise.models import Analise
from apps.documentos.models import Documento
from apps.diligencias.models import Diligencia
from apps.empresas.models import Empresa
from apps.fornecedores.models import Fornecedores
from apps.lancamentos.models import Lancamento
from apps.prestacao.models import Prestacao
from apps.termos.models import Termos
from apps.metas.models import MetaExecucao

OSC_GROUP_MARKERS = (
    "osc",
    "representante",
    "contador",
    "consultor",
    "gestor financeiro",
)

MESES_PT = (
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
)


def usuario_eh_osc(user) -> bool:
    """Identifica a área padrão sem exigir alteração no modelo de usuário.

    Superusuários e contas internas (staff) entram pela área do órgão público.
    Usuários não staff e grupos explicitamente vinculados à OSC entram pela
    área da organização. O superusuário pode alternar a visão no dashboard.
    """
    if not user or not user.is_authenticated or user.is_superuser:
        return False

    nomes_grupos = " ".join(
        user.groups.values_list("name", flat=True)
    ).casefold()
    if any(marcador in nomes_grupos for marcador in OSC_GROUP_MARKERS):
        return True

    return not user.is_staff


def empresa_do_usuario(user):
    try:
        return user.funcionario.empresa
    except Exception:
        return None


def _normalizar_visao(request) -> str:
    visao_padrao = "osc" if usuario_eh_osc(request.user) else "orgao"
    visao_solicitada = request.GET.get("visao", "").strip().lower()

    # A alternância é uma ferramenta de conferência para administradores.
    if request.user.is_superuser and visao_solicitada in {"orgao", "osc"}:
        return visao_solicitada
    return visao_padrao


def _ler_periodo(request):
    inicio = parse_date(request.GET.get("inicio", ""))
    fim = parse_date(request.GET.get("fim", ""))
    periodo_ajustado = False

    if inicio and fim and inicio > fim:
        inicio, fim = fim, inicio
        periodo_ajustado = True

    return inicio, fim, periodo_ajustado


def _aplicar_empresa(queryset, empresa):
    if empresa is None:
        return queryset
    return queryset.filter(empresa=empresa)


def _aplicar_periodo(queryset, campo: str, inicio, fim):
    filtros = {}
    if inicio:
        filtros[f"{campo}__gte"] = inicio
    if fim:
        filtros[f"{campo}__lte"] = fim
    return queryset.filter(**filtros) if filtros else queryset


def _somar(queryset, campo: str) -> Decimal:
    total = queryset.aggregate(total=Sum(campo)).get("total")
    if total is None:
        return Decimal("0.00")
    return Decimal(str(total))


def _percentual(parte: int | Decimal, total: int | Decimal) -> int:
    if not total:
        return 0
    return max(0, min(100, round((Decimal(parte) / Decimal(total)) * 100)))


def _item_distribuicao(rotulo: str, valor: int, total: int, classe: str):
    return {
        "rotulo": rotulo,
        "valor": valor,
        "percentual": _percentual(valor, total),
        "classe": classe,
    }


def _inicio_mes(data_referencia: date, deslocamento: int) -> date:
    indice = data_referencia.year * 12 + data_referencia.month - 1 + deslocamento
    ano, mes_zero = divmod(indice, 12)
    return date(ano, mes_zero + 1, 1)


def _serie_mensal(querysets: Iterable, meses: int = 6):
    hoje = timezone.localdate()
    primeiro_mes = _inicio_mes(hoje.replace(day=1), -(meses - 1))
    chaves = [_inicio_mes(primeiro_mes, i) for i in range(meses)]
    totais = {chave: 0 for chave in chaves}

    for queryset, campo in querysets:
        dados = (
            queryset.filter(**{f"{campo}__date__gte": primeiro_mes})
            .annotate(mes=TruncMonth(campo))
            .values("mes")
            .annotate(total=Count("id"))
        )
        for item in dados:
            mes = item["mes"]
            if mes is None:
                continue
            chave = date(mes.year, mes.month, 1)
            if chave in totais:
                totais[chave] += item["total"]

    maior = max(totais.values(), default=0)
    serie = []
    for chave in chaves:
        valor = totais[chave]
        serie.append(
            {
                "rotulo": f"{MESES_PT[chave.month - 1]}/{str(chave.year)[-2:]}",
                "valor": valor,
                "percentual": _percentual(valor, maior) if maior else 0,
            }
        )
    return serie


def _filtro_prestacao_por_termo(queryset, termo):
    if termo is None:
        return queryset

    identificadores = [termo.numtermo, termo.termo]
    condicao = Q()
    encontrou = False
    for identificador in identificadores:
        if identificador:
            condicao |= Q(numtermo__iexact=identificador.strip())
            encontrou = True
    return queryset.filter(condicao) if encontrou else queryset.none()


def _resumo_termos(termos, lancamentos, documentos, analises, prestacoes):
    itens = []
    for termo in termos[:6]:
        lancamentos_termo = lancamentos.filter(termo=termo)
        documentos_termo = documentos.filter(termo=termo)
        analises_termo = analises.filter(numtermo=termo)
        prestacoes_termo = _filtro_prestacao_por_termo(prestacoes, termo)
        itens.append(
            {
                "objeto": termo,
                "prestacoes": prestacoes_termo.count(),
                "lancamentos": lancamentos_termo.count(),
                "documentos_pendentes": documentos_termo.filter(
                    status__in=[
                        Documento.Status.PENDENTE,
                        Documento.Status.EM_CONFERENCIA,
                        Documento.Status.COM_PENDENCIA,
                    ]
                ).count(),
                "analises_abertas": analises_termo.filter(concluida=False).count(),
                "valor_lancado": _somar(lancamentos_termo, "valor_documento"),
                "valor_glosado": _somar(lancamentos_termo, "valor_glosa"),
            }
        )
    return itens


def montar_contexto_dashboard(request):
    user = request.user
    visao = _normalizar_visao(request)
    inicio, fim, periodo_ajustado = _ler_periodo(request)
    empresa_vinculada = empresa_do_usuario(user)

    if user.is_superuser:
        empresas_disponiveis = Empresa.objects.all().order_by("nome")
        empresa_selecionada = None
        empresa_id = request.GET.get("empresa", "").strip()
        if empresa_id.isdigit():
            empresa_selecionada = empresas_disponiveis.filter(pk=empresa_id).first()
    else:
        empresas_disponiveis = Empresa.objects.filter(
            pk=empresa_vinculada.pk
        ) if empresa_vinculada else Empresa.objects.none()
        empresa_selecionada = empresa_vinculada

    sem_empresa = not user.is_superuser and empresa_selecionada is None

    termos_opcoes = _aplicar_empresa(
        Termos.objects.select_related("empresa"),
        empresa_selecionada,
    )
    if sem_empresa:
        termos_opcoes = termos_opcoes.none()

    termo_selecionado = None
    termo_id = request.GET.get("termo", "").strip()
    if termo_id.isdigit():
        termo_selecionado = termos_opcoes.filter(pk=termo_id).first()

    termos = termos_opcoes
    prestacoes = _aplicar_empresa(
        Prestacao.objects.select_related("empresa"), empresa_selecionada
    )
    lancamentos = _aplicar_empresa(
        Lancamento.objects.select_related(
            "empresa", "termo", "prestacao", "fornecedor", "analise"
        ),
        empresa_selecionada,
    )
    documentos = _aplicar_empresa(
        Documento.objects.select_related(
            "empresa", "termo", "prestacao", "lancamento", "conferido_por"
        ),
        empresa_selecionada,
    )
    analises = _aplicar_empresa(
        Analise.objects.select_related("empresa", "numtermo", "prestacao"),
        empresa_selecionada,
    )
    fornecedores = _aplicar_empresa(
        Fornecedores.objects.select_related("empresa"), empresa_selecionada
    )
    diligencias = _aplicar_empresa(
        Diligencia.objects.select_related("empresa", "responsavel"), empresa_selecionada
    )

    if sem_empresa:
        prestacoes = prestacoes.none()
        lancamentos = lancamentos.none()
        documentos = documentos.none()
        analises = analises.none()
        fornecedores = fornecedores.none()
        diligencias = diligencias.none()

    # O período é aplicado antes do filtro de termo para que o quadro
    # comparativo continue respeitando os mesmos critérios da tela.
    termos = _aplicar_periodo(termos, "assinatura", inicio, fim)
    lancamentos = _aplicar_periodo(lancamentos, "data_documento", inicio, fim)
    documentos = _aplicar_periodo(documentos, "data_documento", inicio, fim)
    analises = _aplicar_periodo(analises, "criada_em__date", inicio, fim)

    # Base anterior ao filtro de termo, usada no quadro comparativo.
    termos_resumo_base = termos
    prestacoes_resumo_base = prestacoes
    lancamentos_resumo_base = lancamentos
    documentos_resumo_base = documentos
    analises_resumo_base = analises

    if termo_selecionado:
        termos = termos.filter(pk=termo_selecionado.pk)
        prestacoes = _filtro_prestacao_por_termo(
            prestacoes,
            termo_selecionado,
        )
        lancamentos = lancamentos.filter(
            termo=termo_selecionado
        )
        documentos = documentos.filter(
            termo=termo_selecionado
        )
        analises = analises.filter(
            numtermo=termo_selecionado
        )

    metas = MetaExecucao.objects.filter(
        prestacao__in=prestacoes
    )

    # Indicadores principais.
    termos_total = termos.count()
    termos_vigentes = termos.filter(
        Q(status__icontains="vigent")
        | Q(status__icontains="ativ")
        | Q(status__icontains="execu")
    ).count()
    prestacoes_total = prestacoes.count()
    prestacoes_concluidas = prestacoes.filter(concluida=True).count()
    prestacoes_abertas = prestacoes_total - prestacoes_concluidas
    prestacoes_elaboracao = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.ELABORACAO
    ).count()

    prestacoes_enviadas = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.ENVIADA
    ).count()

    prestacoes_recebidas = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.RECEBIDA
    ).count()

    prestacoes_em_analise = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.EM_ANALISE
    ).count()

    prestacoes_em_diligencia = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.DILIGENCIA
    ).count()

    prestacoes_corrigidas = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.CORRIGIDA
    ).count()

    prestacoes_aprovadas = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.APROVADA
    ).count()

    prestacoes_aprovadas_ressalvas = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.APROVADA_RESSALVAS
    ).count()

    prestacoes_reprovadas = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.REPROVADA
    ).count()

    prestacoes_encerradas = prestacoes.filter(
        situacao_workflow=Prestacao.SituacaoWorkflow.ENCERRADA
    ).count()


    metas_total = metas.count()

    metas_nao_iniciadas = metas.filter(
        situacao=MetaExecucao.Situacao.NAO_INICIADA
    ).count()

    metas_em_andamento = metas.filter(
        situacao=MetaExecucao.Situacao.EM_ANDAMENTO
    ).count()

    metas_atingidas = metas.filter(
        situacao=MetaExecucao.Situacao.ATINGIDA
    ).count()

    metas_parciais = metas.filter(
        situacao=MetaExecucao.Situacao.PARCIAL
    ).count()

    metas_nao_atingidas = metas.filter(
        situacao=MetaExecucao.Situacao.NAO_ATINGIDA
    ).count()

    metas_suspensas = metas.filter(
        situacao=MetaExecucao.Situacao.SUSPENSA
    ).count()

    metas_criticas = metas_parciais + metas_nao_atingidas

    percentual_metas_atingidas = _percentual(
        metas_atingidas,
        metas_total,
    )

    metas_atrasadas = metas.filter(
        fim__lt=timezone.localdate()
    ).exclude(
        situacao__in=[
            MetaExecucao.Situacao.ATINGIDA,
            MetaExecucao.Situacao.SUSPENSA,
        ]
    ).count()

    lancamentos_total = lancamentos.count()
    lancamentos_nao_analisados = lancamentos.filter(
        situacao=Lancamento.Situacao.NAO_ANALISADO
    ).count()
    lancamentos_regulares = lancamentos.filter(
        situacao=Lancamento.Situacao.REGULAR
    ).count()
    lancamentos_ressalva = lancamentos.filter(
        situacao=Lancamento.Situacao.RESSALVA
    ).count()
    lancamentos_reprovados = lancamentos.filter(
        situacao=Lancamento.Situacao.REPROVADO
    ).count()
    lancamentos_glosados = lancamentos.filter(
        situacao=Lancamento.Situacao.GLOSADO
    ).count()

    documentos_total = documentos.count()
    documentos_pendentes = documentos.filter(
        status__in=[Documento.Status.PENDENTE, Documento.Status.EM_CONFERENCIA]
    ).count()
    documentos_conferidos = documentos.filter(
        status=Documento.Status.CONFERIDO
    ).count()
    documentos_com_pendencia = documentos.filter(
        status=Documento.Status.COM_PENDENCIA
    ).count()
    documentos_reprovados = documentos.filter(
        status=Documento.Status.REPROVADO
    ).count()

    analises_total = analises.count()
    analises_abertas = analises.filter(concluida=False).count()
    analises_concluidas = analises_total - analises_abertas

    hoje = timezone.localdate()
    diligencias_abertas = diligencias.exclude(
        status__in=[
            Diligencia.Status.ATENDIDA,
            Diligencia.Status.NAO_ATENDIDA,
            Diligencia.Status.CANCELADA,
        ]
    )
    diligencias_pendentes = diligencias_abertas.count()
    diligencias_vencidas = diligencias_abertas.filter(
        prazo_resposta__lt=hoje

    ).count()
    limite_proximos_7_dias = hoje + timedelta(days=7)

    diligencias_proximas_vencimento = diligencias_abertas.filter(
        prazo_resposta__gte=hoje,
        prazo_resposta__lte=limite_proximos_7_dias,
    ).count()

    diligencias_urgentes = diligencias_abertas.filter(
        prioridade=Diligencia.Prioridade.URGENTE
    ).count()

    diligencias_respondidas = diligencias.filter(
        status__in=[Diligencia.Status.RESPONDIDA, Diligencia.Status.REANALISE]
    ).count()

    valor_lancado = _somar(lancamentos, "valor_documento")
    valor_glosado = _somar(lancamentos, "valor_glosa")
    valor_analisado = _somar(
        lancamentos.exclude(situacao=Lancamento.Situacao.NAO_ANALISADO),
        "valor_documento",
    )
    valor_aprovado = max(valor_analisado - valor_glosado, Decimal("0.00"))
    valor_global = _somar(termos, "valorglobal")
    valor_repassado = _somar(termos, "valorrepasse")
    saldo_termos = _somar(termos, "valorsaldo")

    valor_executado = valor_lancado

    saldo_a_executar = max(
        valor_global - valor_executado,
        Decimal("0.00"),
    )

    percentual_execucao = _percentual(
        valor_executado,
        valor_global,
    )

    distribuicao_lancamentos = [
        _item_distribuicao(
            "Não analisados", lancamentos_nao_analisados, lancamentos_total, "neutro"
        ),
        _item_distribuicao(
            "Regulares", lancamentos_regulares, lancamentos_total, "sucesso"
        ),
        _item_distribuicao(
            "Com ressalva", lancamentos_ressalva, lancamentos_total, "alerta"
        ),
        _item_distribuicao(
            "Reprovados", lancamentos_reprovados, lancamentos_total, "perigo"
        ),
        _item_distribuicao(
            "Glosados", lancamentos_glosados, lancamentos_total, "roxo"
        ),
    ]
    distribuicao_documentos = [
        _item_distribuicao(
            "Pendentes", documentos_pendentes, documentos_total, "neutro"
        ),
        _item_distribuicao(
            "Conferidos", documentos_conferidos, documentos_total, "sucesso"
        ),
        _item_distribuicao(
            "Com pendência", documentos_com_pendencia, documentos_total, "alerta"
        ),
        _item_distribuicao(
            "Reprovados", documentos_reprovados, documentos_total, "perigo"
        ),
    ]

    alertas = [
        {
            "rotulo": "Diligências vencidas",
            "valor": diligencias_vencidas,
            "icone": "fa-comments-o",
            "classe": "perigo" if diligencias_vencidas else "sucesso",
            "url_name": "list_diligencias",
        },
        {
            "rotulo": "Metas atrasadas",
            "valor": metas_atrasadas,
            "icone": "fa-flag",
            "classe": "perigo" if metas_atrasadas else "sucesso",
            "url_name": "metas_painel",
        },
        {
            "rotulo": "Diligências urgentes em aberto",
            "valor": diligencias_urgentes,
            "icone": "fa-bolt",
            "classe": "perigo" if diligencias_urgentes else "sucesso",
            "url_name": "list_diligencias",
        },
        {
            "rotulo": "Documentos com problema",
            "valor": documentos_com_pendencia + documentos_reprovados,
            "icone": "fa-exclamation-triangle",
            "classe": "perigo"
            if documentos_com_pendencia + documentos_reprovados
            else "sucesso",
            "url_name": "list_documentos",
        },
        {
            "rotulo": "Prestações em diligência",
            "valor": prestacoes_em_diligencia,
            "icone": "fa-folder-open-o",
            "classe": "alerta" if prestacoes_em_diligencia else "sucesso",
            "url_name": "list_prestacao",
        },
        {
            "rotulo": "Diligências vencendo em até 7 dias",
            "valor": diligencias_proximas_vencimento,
            "icone": "fa-clock-o",
            "classe": "alerta" if diligencias_proximas_vencimento else "sucesso",
            "url_name": "list_diligencias",
        },
        {
            "rotulo": "Lançamentos aguardando análise",
            "valor": lancamentos_nao_analisados,
            "icone": "fa-list-alt",
            "classe": "alerta" if lancamentos_nao_analisados else "sucesso",
            "url_name": "list_lancamentos",
        },
        {
            "rotulo": "Documentos aguardando conferência",
            "valor": documentos_pendentes,
            "icone": "fa-files-o",
            "classe": "alerta" if documentos_pendentes else "sucesso",
            "url_name": "list_documentos",
        },
        {
            "rotulo": "Análises técnicas em aberto",
            "valor": analises_abertas,
            "icone": "fa-search",
            "classe": "roxo" if analises_abertas else "sucesso",
            "url_name": "list_analise",
        },
    ]
    prioridades_ativas = sum(1 for alerta in alertas if alerta["valor"] > 0)
    atividade_mensal = _serie_mensal(
        [
            (lancamentos, "criado_em"),
            (documentos, "criado_em"),
            (analises, "criada_em"),
        ]
    )

    contexto = {
        "visao_dashboard": visao,
        "usuario_area_osc": visao == "osc",
        "area_portal": "Área da OSC" if visao == "osc" else "Área do Órgão Público",
        "titulo_dashboard": (
            "Painel da Organização da Sociedade Civil"
            if visao == "osc"
            else "Painel Gerencial do Órgão Público"
        ),
        "descricao_dashboard": (
            "Acompanhe a preparação da prestação de contas, documentos, lançamentos e pendências da sua organização."
            if visao == "osc"
            else "Acompanhe a execução, a análise e a conformidade das parcerias sob responsabilidade do órgão público."
        ),
        "empresas_disponiveis": empresas_disponiveis,
        "empresa_selecionada": empresa_selecionada,
        "termos_disponiveis": termos_opcoes,
        "termo_selecionado": termo_selecionado,
        "inicio_filtro": inicio,
        "fim_filtro": fim,
        "periodo_ajustado": periodo_ajustado,
        "sem_empresa_vinculada": sem_empresa,
        "escopo_todas_empresas": user.is_superuser and empresa_selecionada is None,
        "oscs_total": (
            1 if empresa_selecionada else empresas_disponiveis.count()
        ),
        "fornecedores_total": fornecedores.count(),
        "termos_total": termos_total,
        "termos_vigentes": termos_vigentes,
        "prestacoes_total": prestacoes_total,
        "prestacoes_abertas": prestacoes_abertas,
        "prestacoes_concluidas": prestacoes_concluidas,
        "prestacoes_elaboracao": prestacoes_elaboracao,
        "prestacoes_enviadas": prestacoes_enviadas,
        "prestacoes_recebidas": prestacoes_recebidas,
        "prestacoes_em_analise": prestacoes_em_analise,
        "prestacoes_em_diligencia": prestacoes_em_diligencia,
        "prestacoes_corrigidas": prestacoes_corrigidas,
        "prestacoes_aprovadas": prestacoes_aprovadas,
        "prestacoes_aprovadas_ressalvas": prestacoes_aprovadas_ressalvas,
        "prestacoes_reprovadas": prestacoes_reprovadas,
        "prestacoes_encerradas": prestacoes_encerradas,
        "metas_total": metas_total,
        "metas_nao_iniciadas": metas_nao_iniciadas,
        "metas_em_andamento": metas_em_andamento,
        "metas_atingidas": metas_atingidas,
        "metas_parciais": metas_parciais,
        "metas_nao_atingidas": metas_nao_atingidas,
        "metas_suspensas": metas_suspensas,
        "metas_criticas": metas_criticas,
        "metas_atrasadas": metas_atrasadas,
        "percentual_metas_atingidas": percentual_metas_atingidas,
        "lancamentos_total": lancamentos_total,
        "lancamentos_nao_analisados": lancamentos_nao_analisados,
        "lancamentos_analisados": lancamentos_total - lancamentos_nao_analisados,
        "lancamentos_regulares": lancamentos_regulares,
        "lancamentos_ressalva": lancamentos_ressalva,
        "lancamentos_reprovados": lancamentos_reprovados,
        "lancamentos_glosados": lancamentos_glosados,
        "documentos_total": documentos_total,
        "documentos_pendentes": documentos_pendentes,
        "documentos_conferidos": documentos_conferidos,
        "documentos_com_pendencia": documentos_com_pendencia,
        "documentos_reprovados": documentos_reprovados,
        "analises_total": analises_total,
        "analises_abertas": analises_abertas,
        "analises_concluidas": analises_concluidas,
        "diligencias_pendentes": diligencias_pendentes,
        "diligencias_vencidas": diligencias_vencidas,
        "diligencias_respondidas": diligencias_respondidas,
        "diligencias_proximas_vencimento": diligencias_proximas_vencimento,
        "diligencias_urgentes": diligencias_urgentes,
        "valor_lancado": valor_lancado,
        "valor_analisado": valor_analisado,
        "valor_glosado": valor_glosado,
        "valor_aprovado": valor_aprovado,
        "valor_global": valor_global,
        "valor_repassado": valor_repassado,
        "saldo_termos": saldo_termos,
        "valor_executado": valor_executado,
        "saldo_a_executar": saldo_a_executar,
        "percentual_execucao": percentual_execucao,
        "percentual_documentos": _percentual(documentos_conferidos, documentos_total),
        "percentual_lancamentos": _percentual(
            lancamentos_total - lancamentos_nao_analisados, lancamentos_total
        ),
        "percentual_prestacoes": _percentual(
            prestacoes_concluidas, prestacoes_total
        ),
        "distribuicao_lancamentos": distribuicao_lancamentos,
        "distribuicao_documentos": distribuicao_documentos,
        "alertas_dashboard": alertas,
        "prioridades_ativas": prioridades_ativas,
        "atividade_mensal": atividade_mensal,
        "lancamentos_recentes": lancamentos.order_by("-atualizado_em")[:6],
        "documentos_recentes": documentos.order_by("-atualizado_em")[:6],
        "analises_recentes": analises.order_by("concluida", "-atualizada_em")[:6],
        "resumo_termos": _resumo_termos(
            termos_resumo_base.order_by("-assinatura", "-id"),
            lancamentos_resumo_base,
            documentos_resumo_base,
            analises_resumo_base,
            prestacoes_resumo_base,
        ),
    }
    return contexto





