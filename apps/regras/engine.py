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

    def analisar_verbas_rh(self, folha, contexto=None):
        from apps.regras.rh_verbas import analisar_verbas_rh

        contexto = contexto or ContextoRegras()

        return analisar_verbas_rh(
            folha=folha,
            contexto=contexto,
        )

    def analisar_lgpd_rh(
        self,
        funcionario,
        contexto=None,
        *,
        uso_ia=False,
        dados_minimizados=False,
    ):
        from apps.regras.lgpd_rh import analisar_lgpd_rh

        contexto = contexto or ContextoRegras()

        return analisar_lgpd_rh(
            funcionario=funcionario,
            contexto=contexto,
            uso_ia=uso_ia,
            dados_minimizados=dados_minimizados,
        )

    def analisar_rh_completo(
        self,
        folha,
        contexto=None,
        *,
        uso_ia=False,
        dados_minimizados=False,
    ):
        from apps.regras.rh_consolidado import analisar_rh_completo

        contexto = contexto or ContextoRegras()

        return analisar_rh_completo(
            folha=folha,
            contexto=contexto,
            uso_ia=uso_ia,
            dados_minimizados=dados_minimizados,
        )

    def analisar_execucao_item_plano(
        self,
        item,
        contexto=None,
    ):
        from apps.regras.plano_execucao import (
            analisar_execucao_item_plano,
        )

        contexto = contexto or ContextoRegras()

        return analisar_execucao_item_plano(
            item=item,
            contexto=contexto,
        )

    def analisar_execucao_quantitativa_item(
        self,
        item,
        contexto=None,
    ):
        from apps.regras.plano_quantitativo import (
            analisar_execucao_quantitativa_item,
        )

        contexto = contexto or ContextoRegras()

        return analisar_execucao_quantitativa_item(
            item=item,
            contexto=contexto,
        )

    def analisar_execucao_temporal_item(
        self,
        item,
        contexto=None,
    ):
        from apps.regras.plano_temporal import (
            analisar_execucao_temporal_item,
        )

        contexto = contexto or ContextoRegras()

        return analisar_execucao_temporal_item(
            item=item,
            contexto=contexto,
        )

    def analisar_meta_objeto_item(
        self,
        item,
        contexto=None,
    ):
        from apps.regras.plano_meta_objeto import (
            analisar_meta_objeto_item,
        )

        contexto = contexto or ContextoRegras()

        return analisar_meta_objeto_item(
            item=item,
            contexto=contexto,
        )

    def analisar_item_plano_completo(
        self,
        item,
        contexto=None,
    ):
        from apps.regras.plano_item_consolidado import (
            analisar_item_plano_completo,
        )

        contexto = contexto or ContextoRegras()

        return analisar_item_plano_completo(
            item=item,
            contexto=contexto,
        )

    def analisar_plano_trabalho_completo(
        self,
        plano,
        contexto=None,
    ):
        from apps.regras.plano_consolidado import (
            analisar_plano_trabalho_completo,
        )

        contexto = contexto or ContextoRegras()

        return analisar_plano_trabalho_completo(
            plano=plano,
            contexto=contexto,
        )

motor_regras = MotorRegrasPGP()














