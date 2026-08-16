from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoRegra:
    codigo: str
    severidade: str
    titulo: str
    descricao: str

    regra: str = ""
    categoria: str = "documental"
    resultado: str = "achado"
    fato_verificado: str = ""
    evidencia: str = ""
    fundamentacao: str = ""
    risco_glosa: str = ""
    recomendacao: str = ""
    origem_normativa: str = ""

    def como_dict(self):
        return {
            "codigo": self.codigo,
            "severidade": self.severidade,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "regra": self.regra,
            "categoria": self.categoria,
            "resultado": self.resultado,
            "fato_verificado": self.fato_verificado,
            "evidencia": self.evidencia,
            "fundamentacao": self.fundamentacao,
            "risco_glosa": self.risco_glosa,
            "recomendacao": self.recomendacao,
            "origem_normativa": self.origem_normativa,
        }
