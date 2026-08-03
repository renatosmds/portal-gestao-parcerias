MODULOS = [
    {
        "slug": "primeiros-passos", "titulo": "Primeiros passos", "icone": "fa-compass",
        "resumo": "Conheça o menu, os perfis e o botão de ajuda 5W2H.",
        "perfis": ["todos"],
        "passos": [
            "Identifique sua área no topo da tela.",
            "Use o menu lateral para acessar os módulos.",
            "Clique no botão ? ao lado de um campo para abrir a orientação 5W2H.",
            "Consulte notificações no ícone de sino.",
            "Use esta Central para acompanhar seu progresso.",
        ],
    },
    {
        "slug": "oscs-parcerias", "titulo": "OSCs e parcerias", "icone": "fa-handshake-o",
        "resumo": "Cadastre a organização e formalize a parceria.", "perfis": ["orgao", "administrador"],
        "passos": ["Cadastre ou localize a OSC.", "Confira CNPJ, representante e contatos.", "Cadastre a parceria.", "Vincule a parceria ao órgão e à OSC.", "Revise os dados antes de salvar."],
    },
    {
        "slug": "termos", "titulo": "Termos", "icone": "fa-file-text-o",
        "resumo": "Registre objeto, vigência, valores e instrumento jurídico.", "perfis": ["orgao", "administrador"],
        "passos": ["Abra Termos e clique em Novo Termo.", "Selecione a parceria.", "Informe número, tipo e objeto.", "Preencha vigência e valores.", "Salve e confira o resumo."],
    },
    {
        "slug": "prestacao", "titulo": "Prestação de contas", "icone": "fa-folder-open-o",
        "resumo": "Prepare, envie, receba e acompanhe a prestação.", "perfis": ["orgao", "osc"],
        "passos": ["Crie a prestação para a competência correta.", "Registre lançamentos e documentos.", "Faça a pré-conferência.", "Envie ao órgão público.", "Acompanhe a situação e as diligências."],
    },
    {
        "slug": "documentos-lancamentos", "titulo": "Documentos e lançamentos", "icone": "fa-files-o",
        "resumo": "Registre despesas e vincule os comprovantes.", "perfis": ["orgao", "osc"],
        "passos": ["Cadastre o lançamento.", "Informe fornecedor, data e valor.", "Anexe documento fiscal e comprovante.", "Vincule os documentos ao lançamento.", "Revise valores e datas."],
    },
    {
        "slug": "conciliacao", "titulo": "Conciliação bancária", "icone": "fa-exchange",
        "resumo": "Compare extrato, pagamentos e lançamentos.", "perfis": ["orgao", "osc"],
        "passos": ["Crie a conciliação da prestação.", "Importe ou registre movimentações.", "Vincule movimentações aos lançamentos.", "Analise divergências.", "Confira o saldo final calculado."],
    },
    {
        "slug": "analise-diligencia", "titulo": "Análise e diligência", "icone": "fa-search",
        "resumo": "Analise, solicite esclarecimentos e registre conclusões.", "perfis": ["orgao"],
        "passos": ["Abra a prestação recebida.", "Confira documentos, valores e metas.", "Use a Análise Assistida como apoio.", "Emita diligência quando necessário.", "Reanalise a resposta e registre a conclusão."],
    },
    {
        "slug": "metas", "titulo": "Metas e indicadores", "icone": "fa-bullseye",
        "resumo": "Acompanhe resultados físicos e percentuais de execução.", "perfis": ["orgao", "osc"],
        "passos": ["Cadastre a meta.", "Defina unidade e valor previsto.", "Atualize o realizado.", "Justifique execução parcial.", "Confira o percentual calculado."],
    },
    {
        "slug": "transparencia", "titulo": "Transparência", "icone": "fa-eye",
        "resumo": "Classifique e publique apenas informações autorizadas.", "perfis": ["orgao", "administrador"],
        "passos": ["Revise os dados da parceria.", "Classifique documentos.", "Marque apenas itens públicos.", "Publique a parceria.", "Confira a visão pública em janela anônima."],
    },
    {
        "slug": "seguranca", "titulo": "Segurança e LGPD", "icone": "fa-shield",
        "resumo": "Use perfis, permissões e dados de forma segura.", "perfis": ["todos"],
        "passos": ["Use conta individual.", "Não compartilhe senhas.", "Evite anexar dados desnecessários.", "Confira a classificação do documento.", "Comunique acessos ou exposições indevidas."],
    },
]

FAQ = [
    ("Onde encontro ajuda para um campo?", "Clique no pequeno botão ? ao lado do rótulo do campo."),
    ("Por que alguns campos não mostram o botão?", "A ajuda aparece quando existe orientação compatível e ativa. A base pode ser ampliada pelo administrador."),
    ("A Análise Assistida decide a prestação?", "Não. Ela apresenta alertas e rascunhos, sempre sujeitos à revisão humana."),
    ("Quem pode publicar na transparência?", "Somente usuários autorizados do órgão público ou administradores."),
    ("Posso alterar uma prestação já enviada?", "Depende da situação e das permissões configuradas. Em geral, alterações após envio são controladas."),
]


def obter_modulo(slug):
    return next((m for m in MODULOS if m["slug"] == slug), None)
