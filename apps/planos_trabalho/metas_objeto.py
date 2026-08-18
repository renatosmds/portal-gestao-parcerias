import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal

from apps.planos_trabalho.models import (
    VinculoLancamentoItemPlano,
)


PALAVRAS_IGNORADAS = {
    "para",
    "pela",
    "pelo",
    "pelos",
    "pelas",
    "com",
    "sem",
    "uma",
    "umas",
    "uns",
    "dos",
    "das",
    "que",
    "ser",
    "sua",
    "suas",
    "seu",
    "seus",
    "este",
    "esta",
    "esses",
    "essas",
    "entre",
    "sobre",
    "atraves",
    "execucao",
    "realizacao",
}


def normalizar_identificador(valor):
    if valor is None:
        return ""

    return re.sub(
        r"[^0-9a-z]",
        "",
        str(valor).strip().lower(),
    )


def _normalizar_texto(valor):
    texto = str(valor or "").lower()

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(
            caractere
        )
    )

    return texto


def _tokens(valor):
    texto = _normalizar_texto(
        valor
    )

    palavras = re.findall(
        r"[a-z0-9]+",
        texto,
    )

    return {
        palavra
        for palavra in palavras
        if (
            len(palavra) >= 4
            and palavra
            not in PALAVRAS_IGNORADAS
        )
    }


def _decimal(valor):
    return Decimal(
        str(valor or 0)
    ).quantize(
        Decimal("0.01")
    )


@dataclass(frozen=True)
class ResumoMetaObjetoItem:
    item_id: int

    termo_id: object
    termo_numero: str
    termo_empresa_id: object
    objeto: str

    meta_id: object
    meta_codigo: str
    meta_titulo: str
    meta_descricao: str
    meta_situacao: str
    meta_valor_previsto: Decimal
    meta_valor_realizado: Decimal

    prestacao_id: object
    prestacao_numtermo: str
    prestacao_empresa_id: object

    quantidade_lancamentos: int
    valor_lancamentos: Decimal

    tokens_despesa: frozenset = field(
        default_factory=frozenset
    )

    tokens_meta: frozenset = field(
        default_factory=frozenset
    )

    tokens_objeto: frozenset = field(
        default_factory=frozenset
    )

    @property
    def possui_meta(self):
        return self.meta_id is not None

    @property
    def empresa_compativel(self):
        if not self.possui_meta:
            return None

        if (
            self.termo_empresa_id is None
            or self.prestacao_empresa_id is None
        ):
            return None

        return (
            self.termo_empresa_id
            == self.prestacao_empresa_id
        )

    @property
    def numero_termo_compativel(self):
        if not self.possui_meta:
            return None

        termo = normalizar_identificador(
            self.termo_numero
        )

        prestacao = normalizar_identificador(
            self.prestacao_numtermo
        )

        if not termo or not prestacao:
            return None

        return termo == prestacao

    @property
    def intersecao_despesa_meta(self):
        return (
            self.tokens_despesa
            & self.tokens_meta
        )

    @property
    def intersecao_meta_objeto(self):
        return (
            self.tokens_meta
            & self.tokens_objeto
        )

    @property
    def possui_evidencia_textual_despesa_meta(
        self,
    ):
        return bool(
            self.intersecao_despesa_meta
        )

    @property
    def possui_evidencia_textual_meta_objeto(
        self,
    ):
        return bool(
            self.intersecao_meta_objeto
        )


def resumo_meta_objeto_item(item):
    plano = item.plano
    termo = plano.termo

    meta = item.meta

    prestacao = (
        meta.prestacao
        if meta is not None
        else None
    )

    vinculos = list(
        VinculoLancamentoItemPlano.objects
        .filter(
            item_plano=item,
            ativo=True,
        )
        .select_related(
            "lancamento",
        )
    )

    descricoes_lancamentos = []

    valor_lancamentos = Decimal(
        "0.00"
    )

    for vinculo in vinculos:
        lancamento = vinculo.lancamento

        descricoes_lancamentos.append(
            str(
                getattr(
                    lancamento,
                    "descricao",
                    "",
                )
                or ""
            )
        )

        valor_lancamentos += _decimal(
            getattr(
                lancamento,
                "valor_documento",
                None,
            )
        )

    texto_despesa = " ".join(
        [
            str(
                item.descricao
                or ""
            ),
            str(
                item.rubrica_nivel_1
                or ""
            ),
            str(
                item.rubrica_nivel_2
                or ""
            ),
            str(
                item.rubrica_nivel_3
                or ""
            ),
            *descricoes_lancamentos,
        ]
    )

    texto_meta = ""

    if meta is not None:
        texto_meta = " ".join(
            [
                str(
                    meta.titulo
                    or ""
                ),
                str(
                    meta.descricao
                    or ""
                ),
            ]
        )

    objeto = str(
        getattr(
            termo,
            "objeto",
            "",
        )
        or ""
    )

    return ResumoMetaObjetoItem(
        item_id=item.pk,

        termo_id=termo.pk,
        termo_numero=str(
            termo.numtermo
            or ""
        ),
        termo_empresa_id=(
            termo.empresa_id
        ),
        objeto=objeto,

        meta_id=(
            meta.pk
            if meta is not None
            else None
        ),
        meta_codigo=(
            str(
                meta.codigo
                or ""
            )
            if meta is not None
            else ""
        ),
        meta_titulo=(
            str(
                meta.titulo
                or ""
            )
            if meta is not None
            else ""
        ),
        meta_descricao=(
            str(
                meta.descricao
                or ""
            )
            if meta is not None
            else ""
        ),
        meta_situacao=(
            str(
                meta.situacao
                or ""
            )
            if meta is not None
            else ""
        ),
        meta_valor_previsto=(
            _decimal(
                meta.valor_previsto
            )
            if meta is not None
            else Decimal("0.00")
        ),
        meta_valor_realizado=(
            _decimal(
                meta.valor_realizado
            )
            if meta is not None
            else Decimal("0.00")
        ),

        prestacao_id=(
            prestacao.pk
            if prestacao is not None
            else None
        ),
        prestacao_numtermo=(
            str(
                prestacao.numtermo
                or ""
            )
            if prestacao is not None
            else ""
        ),
        prestacao_empresa_id=(
            prestacao.empresa_id
            if prestacao is not None
            else None
        ),

        quantidade_lancamentos=len(
            vinculos
        ),
        valor_lancamentos=(
            valor_lancamentos.quantize(
                Decimal("0.01")
            )
        ),

        tokens_despesa=frozenset(
            _tokens(
                texto_despesa
            )
        ),
        tokens_meta=frozenset(
            _tokens(
                texto_meta
            )
        ),
        tokens_objeto=frozenset(
            _tokens(
                objeto
            )
        ),
    )
