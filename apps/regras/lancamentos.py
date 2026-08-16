from dataclasses import dataclass, field

from apps.documentos.models import Documento
from apps.regras.context import ContextoRegras
from apps.regras.engine import motor_regras
from apps.regras.resultado import ResultadoRegra
from apps.regras.rules.financeiro import avaliar_financeiro_lancamento
from apps.regras.rules.vigencia import avaliar_vigencia_lancamento


@dataclass
class ResultadoAnaliseLancamento:
    lancamento_id: int
    numero_lancamento: str
    achados: list = field(default_factory=list)

    @property
    def total_achados(self):
        return len(self.achados)

    @property
    def criticos(self):
        return [
            item
            for item in self.achados
            if item.severidade == "critico"
        ]

    @property
    def alertas(self):
        return [
            item
            for item in self.achados
            if item.severidade == "alerta"
        ]

    @property
    def informativos(self):
        return [
            item
            for item in self.achados
            if item.severidade == "info"
        ]

    @property
    def possui_risco_glosa(self):
        return any(
            bool(item.risco_glosa)
            for item in self.achados
        )

    @property
    def resultado_preliminar(self):
        """
        Resultado técnico preliminar.

        Não altera a situação do lançamento e não representa
        aprovação, reprovação ou glosa administrativa.
        """

        if self.criticos:
            return "pendencia_critica"

        if self.alertas:
            return "requer_conferencia"

        return "sem_inconsistencia_detectada"


def analisar_lancamento(lancamento, contexto=None):
    contexto = contexto or ContextoRegras()

    achados = []

    documentos = Documento.objects.filter(
        lancamento=lancamento
    ).select_related(
        "empresa",
        "termo",
        "prestacao",
        "lancamento",
    )

    if not documentos.exists():
        achados.append(
            ResultadoRegra(
                codigo="LANC_SEM_DOCUMENTO",
                severidade="critico",
                titulo="Lançamento sem documento vinculado",
                descricao=(
                    "Não foi localizado documento comprobatório "
                    "vinculado ao lançamento."
                ),
                regra="LANC_SEM_DOCUMENTO",
                categoria="documental",
                resultado="achado",
                fato_verificado=(
                    "Ausência de documento vinculado ao lançamento."
                ),
                evidencia=(
                    f"Lançamento {lancamento.numero_lancamento} "
                    "sem registros em Documento."
                ),
                risco_glosa=(
                    "Elevado caso a despesa não possua documentação "
                    "hábil capaz de demonstrar sua regularidade."
                ),
                recomendacao=(
                    "Solicitar e conferir a documentação comprobatória "
                    "antes da conclusão da análise."
                ),
            )
        )

    achados.extend(
        avaliar_financeiro_lancamento(
            lancamento,
            contexto=contexto,
        )
    )

    achados.extend(
        avaliar_vigencia_lancamento(
            lancamento,
            contexto=contexto,
        )
    )

    for documento in documentos:
        resultados_documento = (
            motor_regras.analisar_documento(
                documento,
                contexto=contexto,
            )
        )

        for resultado in resultados_documento:
            if resultado.codigo == "SEM_INCONSISTENCIA_LOCAL":
                continue

            achados.append(resultado)

    return ResultadoAnaliseLancamento(
        lancamento_id=lancamento.pk,
        numero_lancamento=lancamento.numero_lancamento,
        achados=achados,
    )


