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


motor_regras = MotorRegrasPGP()

