CATALOGO_RELATORIOS = {

    # =========================================================
    # GESTAO DAS PARCERIAS
    # =========================================================

    "empresas": {
        "grupo": "Gestão das Parcerias",
        "titulo": "OSCs / Empresas",
        "modelo": "empresas.Empresa",
        "permissao": "empresas.view_empresa",
        "empresa_campo": "pk",
        "colunas": [
            ("id", "Código"),
            ("nome", "OSC / Empresa"),
        ],
    },

    "parcerias": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Parcerias",
        "modelo": "parcerias.Parcerias",
        "permissao": "parcerias.view_parcerias",
        "empresa_campo": "empresa",
        "colunas": [
            ("id", "Código"),
            ("nomeOSC", "OSC"),
            ("numtermo", "Termo"),
            ("status", "Situação"),
            ("prazoFinal", "Prazo final"),
            ("concluido", "Concluída"),
        ],
    },

    "termos": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Termos",
        "modelo": "termos.Termos",
        "permissao": "termos.view_termos",
        "empresa_campo": "empresa",
        "colunas": [
            ("numtermo", "Número"),
            ("empresa", "OSC"),
            ("tipo", "Tipo"),
            ("objeto", "Objeto"),
            ("inicioVigencia", "Início"),
            ("terminoVigencia", "Término"),
            ("valorglobal", "Valor global"),
            ("status", "Situação"),
        ],
    },

    "planos-trabalho": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Planos de Trabalho",
        "modelo": "planos_trabalho.PlanoTrabalho",
        "permissao": "planos_trabalho.view_planotrabalho",
        "empresa_campo": "termo__empresa",
        "colunas": [
            ("id", "Código"),
            ("termo", "Termo"),
            ("versao", "Versão"),
            ("titulo", "Título"),
            ("situacao", "Situação"),
            ("inicio_vigencia", "Início"),
            ("fim_vigencia", "Fim"),
            ("data_aprovacao", "Aprovação"),
        ],
    },

    "itens-plano": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Itens do Plano de Trabalho",
        "modelo": "planos_trabalho.ItemPlanoTrabalho",
        "permissao": "planos_trabalho.view_itemplanotrabalho",
        "empresa_campo": "plano__termo__empresa",
        "colunas": [
            ("codigo", "Código"),
            ("plano", "Plano"),
            ("descricao", "Descrição"),
            ("unidade", "Unidade"),
            ("quantidade_prevista", "Quantidade prevista"),
            ("valor_unitario_previsto", "Valor unitário"),
            ("valor_total_previsto", "Valor previsto"),
            ("meta", "Meta"),
            ("ativo", "Ativo"),
        ],
    },

    "prestacoes": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Prestações de Contas",
        "modelo": "prestacao.Prestacao",
        "permissao": "prestacao.view_prestacao",
        "empresa_campo": "empresa",
        "colunas": [
            ("id", "Código"),
            ("empresa", "OSC"),
            ("numtermo", "Termo"),
            ("tipo", "Tipo"),
            ("situacao_workflow", "Situação"),
            ("analista_responsavel", "Analista"),
            ("concluida", "Concluída"),
            ("valorContrato", "Valor contrato"),
        ],
    },

    "competencias": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Competências das Prestações",
        "modelo": "prestacao.CompetenciaPrestacao",
        "permissao": "prestacao.view_competenciaprestacao",
        "empresa_campo": "prestacao__empresa",
        "colunas": [
            ("prestacao", "Prestação"),
            ("ano", "Ano"),
            ("mes", "Mês"),
            ("saldo_inicial", "Saldo inicial"),
            ("saldo_final", "Saldo final"),
            ("status", "Situação"),
        ],
    },

    "lancamentos": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Lançamentos",
        "modelo": "lancamentos.Lancamento",
        "permissao": "lancamentos.view_lancamento",
        "empresa_campo": "empresa",
        "colunas": [
            ("numero_lancamento", "Lançamento"),
            ("empresa", "OSC"),
            ("termo", "Termo"),
            ("prestacao", "Prestação"),
            ("competencia", "Competência"),
            ("fornecedor", "Fornecedor"),
            ("data_documento", "Data documento"),
            ("descricao", "Descrição"),
            ("valor_documento", "Valor"),
            ("situacao", "Situação"),
        ],
    },

    "documentos": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Documentos",
        "modelo": "documentos.Documento",
        "permissao": "documentos.view_documento",
        "empresa_campo": "empresa",
        "colunas": [
            ("id", "Código"),
            ("empresa", "OSC"),
            ("termo", "Termo"),
            ("prestacao", "Prestação"),
            ("lancamento", "Lançamento"),
            ("tipo", "Tipo"),
            ("numero_documento", "Número"),
            ("descricao", "Descrição"),
            ("data_documento", "Data"),
            ("status", "Situação"),
        ],
    },

    "metas": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Metas",
        "modelo": "metas.MetaExecucao",
        "permissao": "metas.view_metaexecucao",
        "empresa_campo": "prestacao__empresa",
        "colunas": [
            ("codigo", "Código"),
            ("prestacao", "Prestação"),
            ("titulo", "Meta"),
            ("unidade", "Unidade"),
            ("valor_previsto", "Previsto"),
            ("valor_realizado", "Realizado"),
            ("inicio", "Início"),
            ("fim", "Fim"),
            ("situacao", "Situação"),
            ("responsavel", "Responsável"),
        ],
    },

    "pareceres": {
        "grupo": "Gestão das Parcerias",
        "titulo": "Pareceres Técnicos",
        "modelo": "pareceres.ParecerTecnico",
        "permissao": "pareceres.view_parecertecnico",
        "empresa_campo": "empresa",
        "colunas": [
            ("numero", "Número"),
            ("versao", "Versão"),
            ("empresa", "OSC"),
            ("prestacao", "Prestação"),
            ("situacao", "Situação"),
            ("tipo_conclusao", "Conclusão"),
            ("elaborado_por", "Elaborado por"),
            ("elaborado_em", "Elaborado em"),
            ("aprovado_em", "Aprovado em"),
        ],
    },

    # =========================================================
    # FINANCEIRO
    # =========================================================

    "movimentacoes-financeiras": {
        "grupo": "Financeiro",
        "titulo": "Movimentações Financeiras",
        "modelo": "financeiro.MovimentacaoFinanceira",
        "permissao": "financeiro.view_movimentacaofinanceira",
        "empresa_campo": "empresa",
        "colunas": [
            ("data", "Data"),
            ("empresa", "OSC"),
            ("termo", "Termo"),
            ("prestacao", "Prestação"),
            ("competencia", "Competência"),
            ("tipo", "Tipo"),
            ("descricao", "Descrição"),
            ("valor", "Valor"),
        ],
    },

    "importacoes-ofx": {
        "grupo": "Financeiro",
        "titulo": "Importações OFX",
        "modelo": "financeiro.ImportacaoOFX",
        "permissao": "financeiro.view_importacaoofx",
        "empresa_campo": "empresa",
        "colunas": [
            ("id", "Código"),
            ("empresa", "OSC"),
            ("termo", "Termo"),
            ("prestacao", "Prestação"),
            ("nome_arquivo", "Arquivo"),
            ("banco", "Banco"),
            ("conta_mascarada", "Conta"),
            ("data_inicio", "Período inicial"),
            ("data_fim", "Período final"),
            ("saldo_informado", "Saldo"),
            ("quantidade_movimentos", "Movimentos"),
            ("importado_em", "Importado em"),
        ],
    },

    "conciliacoes-financeiras": {
        "grupo": "Financeiro",
        "titulo": "Conciliações Financeiras",
        "modelo": "financeiro.ConciliacaoFinanceira",
        "permissao": "financeiro.view_conciliacaofinanceira",
        "empresa_campo": "movimentacao__empresa",
        "colunas": [
            ("id", "Código"),
            ("movimentacao", "Movimentação"),
            ("lancamento", "Lançamento"),
            ("status", "Situação"),
            ("decidido_por", "Decidido por"),
            ("decidido_em", "Decidido em"),
        ],
    },

    "conciliacao-bancaria": {
        "grupo": "Financeiro",
        "titulo": "Conciliação Bancária",
        "modelo": "conciliacao.Conciliacao",
        "permissao": "conciliacao.view_conciliacao",
        "empresa_campo": "prestacao__empresa",
        "colunas": [
            ("id", "Código"),
            ("prestacao", "Prestação"),
            ("saldo_inicial", "Saldo inicial"),
            ("saldo_final_informado", "Saldo final"),
            ("situacao", "Situação"),
            ("criado_em", "Criado em"),
        ],
    },

    "ocorrencias-conciliacao": {
        "grupo": "Financeiro",
        "titulo": "Ocorrências de Conciliação",
        "modelo": "conciliacao.OcorrenciaConciliacao",
        "permissao": "conciliacao.view_ocorrenciaconciliacao",
        "empresa_campo": "conciliacao__prestacao__empresa",
        "colunas": [
            ("id", "Código"),
            ("conciliacao", "Conciliação"),
            ("movimentacao", "Movimentação"),
            ("tipo", "Tipo"),
            ("descricao", "Descrição"),
            ("situacao", "Situação"),
            ("criado_em", "Criado em"),
        ],
    },

    "fornecedores": {
        "grupo": "Financeiro",
        "titulo": "Fornecedores",
        "modelo": "fornecedores.Fornecedores",
        "permissao": "fornecedores.view_fornecedores",
        "empresa_campo": "empresa",
        "colunas": [
            ("credor", "Credor"),
            ("razao", "Razão social"),
            ("fantasia", "Nome fantasia"),
            ("pessoa", "Pessoa"),
            ("tipo", "Documento"),
            ("numero", "Número"),
            ("empresa", "OSC"),
            ("cidade", "Cidade"),
            ("estado", "UF"),
        ],
    },

    # =========================================================
    # PESSOAS E ADMINISTRATIVO
    # =========================================================

    "departamentos": {
        "grupo": "Pessoas e Administrativo",
        "titulo": "Estrutura Organizacional",
        "modelo": "departamentos.Departamento",
        "permissao": "departamentos.view_departamento",
        "empresa_campo": "empresa",
        "colunas": [
            ("id", "Código"),
            ("empresa", "Empresa"),
            ("nome", "Unidade"),
            ("tipo", "Tipo"),
            ("superior", "Unidade superior"),
        ],
    },

    "ponto": {
        "grupo": "Pessoas e Administrativo",
        "titulo": "Folhas de Ponto",
        "modelo": "funcionarios.FolhaPonto",
        "permissao": "funcionarios.view_folhaponto",
        "empresa_campo": "funcionario__empresa",
        "colunas": [
            ("funcionario", "Funcionário"),
            ("competencia", "Competência"),
            ("horas_previstas", "Previstas"),
            ("horas_trabalhadas", "Trabalhadas"),
            ("horas_extras", "Extras"),
            ("horas_faltas_atrasos", "Faltas/Atrasos"),
            ("banco_horas", "Banco"),
            ("status", "Situação"),
        ],
    },

    "horas-extras": {
        "grupo": "Pessoas e Administrativo",
        "titulo": "Banco / Horas Extras",
        "modelo": "registro_hora_extra.RegistroHoraExtra",
        "permissao": "registro_hora_extra.view_registrohoraextra",
        "empresa_campo": "empresa",
        "colunas": [
            ("id", "Código"),
            ("empresa", "Empresa"),
            ("funcionario", "Funcionário"),
            ("assunto", "Assunto"),
            ("motivo", "Motivo"),
            ("horas", "Horas"),
            ("utilizada", "Utilizada"),
        ],
    },

    # =========================================================
    # OPERACAO DO PORTAL
    # =========================================================

    "importacoes": {
        "grupo": "Operação do Portal",
        "titulo": "Histórico de Importações",
        "modelo": "importacoes.Importacao",
        "permissao": "importacoes.view_importacao",
        "empresa_campo": None,
        "colunas": [
            ("id", "Código"),
            ("tipo", "Tipo"),
            ("arquivo_nome", "Arquivo"),
            ("sistema_origem", "Origem"),
            ("situacao", "Situação"),
            ("total_lido", "Lidos"),
            ("total_novos", "Novos"),
            ("total_atualizados", "Atualizados"),
            ("total_duplicados", "Duplicados"),
            ("total_erros", "Erros"),
            ("criado_por", "Criado por"),
            ("criado_em", "Criado em"),
        ],
    },

    "transparencia-parcerias": {
        "grupo": "Operação do Portal",
        "titulo": "Transparência das Parcerias",
        "modelo": "transparencia.PublicacaoParceria",
        "permissao": "transparencia.view_publicacaoparceria",
        "empresa_campo": "termo__empresa",
        "colunas": [
            ("termo", "Termo"),
            ("publicada", "Publicada"),
            ("orgao_responsavel", "Órgão"),
            ("publicada_em", "Publicada em"),
            ("motivo_restricao", "Restrição"),
        ],
    },

    "transparencia-documentos": {
        "grupo": "Operação do Portal",
        "titulo": "Transparência dos Documentos",
        "modelo": "transparencia.PublicacaoDocumento",
        "permissao": "transparencia.view_publicacaodocumento",
        "empresa_campo": "documento__empresa",
        "colunas": [
            ("documento", "Documento"),
            ("classificacao", "Classificação"),
            ("publicado", "Publicado"),
            ("titulo_publico", "Título"),
            ("publicado_em", "Publicado em"),
            ("motivo_restricao", "Restrição"),
        ],
    },

    "suporte": {
        "grupo": "Operação do Portal",
        "titulo": "Chamados de Suporte",
        "modelo": "suporte.ChamadoSuporte",
        "permissao": "suporte.view_chamadosuporte",
        "empresa_campo": None,
        "colunas": [
            ("id", "Código"),
            ("solicitante", "Solicitante"),
            ("assunto", "Assunto"),
            ("categoria", "Categoria"),
            ("prioridade", "Prioridade"),
            ("situacao", "Situação"),
            ("responsavel", "Responsável"),
            ("criado_em", "Criado em"),
            ("encerrado_em", "Encerrado em"),
        ],
    },

    "treinamento": {
        "grupo": "Operação do Portal",
        "titulo": "Progresso de Treinamento",
        "modelo": "treinamento.ProgressoTreinamento",
        "permissao": "treinamento.view_progressotreinamento",
        "empresa_campo": None,
        "colunas": [
            ("usuario", "Usuário"),
            ("modulo", "Módulo"),
            ("concluido", "Concluído"),
            ("atualizado_em", "Atualizado em"),
        ],
    },

    "cursos": {
        "grupo": "Operação do Portal",
        "titulo": "Cursos",
        "modelo": "curso.Curso",
        "permissao": "curso.view_curso",
        "empresa_campo": None,
        "colunas": [
            ("id", "Código"),
            ("nomeCurso", "Curso"),
            ("mesCurso", "Mês"),
            ("anoCurso", "Ano"),
            ("cronograma", "Cronograma"),
            ("horario", "Horário"),
            ("carga", "Carga horária"),
            ("docente", "Docente"),
        ],
    },
}
