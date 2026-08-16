from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class FonteNormativa:
    """
    Referência normativa aplicável a uma análise.

    escopo:
        nacional
        estadual
        municipal
        orgao
        instrumento
    """

    codigo: str
    titulo: str
    escopo: str
    referencia: str = ""
    ente: str = ""
    vigente: bool = True


@dataclass(frozen=True)
class ContextoRegras:
    """
    Contexto institucional e normativo do PGP Rules.

    Nenhuma norma local deve ser aplicada sem que pertença
    explicitamente ao tenant/ente analisado.
    """

    tenant: Optional[Any] = None
    municipio: Optional[Any] = None
    orgao: Optional[Any] = None
    usuario: Optional[Any] = None

    fontes_normativas: tuple = field(default_factory=tuple)

    def fontes_por_escopo(self, escopo):
        return tuple(
            fonte
            for fonte in self.fontes_normativas
            if fonte.escopo == escopo
            and fonte.vigente
        )

    @property
    def fontes_nacionais(self):
        return self.fontes_por_escopo("nacional")

    @property
    def fontes_locais(self):
        return tuple(
            fonte
            for fonte in self.fontes_normativas
            if fonte.escopo in {
                "estadual",
                "municipal",
                "orgao",
                "instrumento",
            }
            and fonte.vigente
        )
