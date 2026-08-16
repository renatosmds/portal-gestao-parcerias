from apps.regras.context import ContextoRegras
from apps.regras.rules.documental import avaliar_documento


class MotorRegrasPGP:
    """
    Fachada do motor determinístico de regras do PGP.
    """

    def analisar_documento(self, documento, contexto=None):
        contexto = contexto or ContextoRegras()
        return avaliar_documento(
            documento=documento,
            contexto=contexto,
        )

    def analisar_lancamento(self, lancamento, contexto=None):
        from apps.regras.lancamentos import analisar_lancamento

        contexto = contexto or ContextoRegras()

        return analisar_lancamento(
            lancamento=lancamento,
            contexto=contexto,
        )


    def analisar_folha_pagamento(self, folha, contexto=None):
        from apps.regras.rh import analisar_folha_pagamento

        contexto = contexto or ContextoRegras()

        return analisar_folha_pagamento(
            folha=folha,
            contexto=contexto,
        )

    def analisar_documentacao_rh(self, folha, contexto=None):
        from apps.regras.rh_documentos import analisar_documentacao_rh

        contexto = contexto or ContextoRegras()

        return analisar_documentacao_rh(
            folha=folha,
            contexto=contexto,
        )

    def analisar_conciliacao_rh(self, folha, contexto=None):
        from apps.regras.rh_conciliacao import analisar_conciliacao_rh

        contexto = contexto or ContextoRegras()

        return analisar_conciliacao_rh(
            folha=folha,
            contexto=contexto,
        )

    def analisar_composicao_rh(self, folha, contexto=None):
        from apps.regras.rh_composicao import analisar_composicao_rh

        contexto = contexto or ContextoRegras()

        return analisar_composicao_rh(
            folha=folha,
            contexto=contexto,
        )

motor_regras = MotorRegrasPGP()





