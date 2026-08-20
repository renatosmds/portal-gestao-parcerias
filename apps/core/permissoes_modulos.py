from functools import wraps

from django.core.exceptions import PermissionDenied


MODULOS = {
    "empresas": ("empresas.view_empresa",),
    "departamentos": ("departamentos.view_departamento",),
    "fornecedores": ("fornecedores.view_fornecedores",),
    "funcionarios": ("funcionarios.view_funcionario",),
    "folha_ponto": ("funcionarios.view_folhaponto",),
    "folha_pagamento": ("funcionarios.view_folhapagamento",),
    "banco_horas": ("registro_hora_extra.view_registrohoraextra",),
    "execucao": ("conferencia3.view_conferencia3",),
    "financeiro": ("receitas.view_receitas",),
    "diligencias": ("diligencias.view_diligencia",),
    "importacoes": ("importacoes.view_importacao",),
    "conciliacao": ("conciliacao.view_conciliacao",),
    "metas": ("metas.view_metaexecucao",),
    "pareceres": ("pareceres.view_parecertecnico",),
    "planos_trabalho": ("planos_trabalho.view_planotrabalho",),
    "assistente_ia": ("assistente_ia.view_processamentoassistido",),
    "documentos": ("documentos.view_documento",),
    "lancamentos": ("lancamentos.view_lancamento",),
    "analises": ("analise.view_analise",),
    "prestacoes": ("prestacao.view_prestacao",),
    "termos": ("termos.view_termos",),
    "parcerias": ("parcerias.view_parcerias",),
    "treinamento": ("treinamento.view_progressotreinamento",),
    "suporte": ("suporte.view_chamadosuporte",),
    "cursos": ("curso.view_curso",),

    # Relatorios nao possui modelo/permissao propria.
    # O modulo fica disponivel se houver acesso a pelo menos
    # uma das fontes atualmente relatadas pelo aplicativo.
    "relatorios": (
        "diligencias.view_diligencia",
        "lancamentos.view_lancamento",
        "funcionarios.view_funcionario",
        "funcionarios.view_folhapagamento",
    ),
}


def modulo_liberado(user, modulo):
    """
    Informa se o usuario pode acessar um modulo.

    Superusuarios possuem acesso global.
    Para usuarios comuns, basta possuir uma das permissoes
    configuradas para o modulo, diretamente ou por grupo.
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    permissoes = MODULOS.get(modulo, ())

    if not permissoes:
        return False

    return any(user.has_perm(permissao) for permissao in permissoes)


def modulos_liberados(user):
    """Retorna as chaves dos modulos liberados para o usuario."""
    return {
        modulo
        for modulo in MODULOS
        if modulo_liberado(user, modulo)
    }


def exigir_modulo(modulo):
    """
    Decorator para views baseadas em funcao.

    A interface e a URL passam a utilizar a mesma regra central.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not modulo_liberado(request.user, modulo):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
