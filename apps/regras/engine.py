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


motor_regras = MotorRegrasPGP()
