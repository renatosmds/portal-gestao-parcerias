from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import re


@dataclass(frozen=True)
class MovimentoOFX:
    tipo: str
    data_postagem: datetime
    valor: Decimal
    fitid: str
    checknum: str
    memo: str


@dataclass(frozen=True)
class ExtratoOFX:
    versao: str
    charset: str
    moeda: str
    banco: str
    conta: str
    tipo_conta: str
    data_inicio: str
    data_fim: str
    saldo: Decimal
    data_saldo: str
    movimentos: tuple


def _valor_tag(texto, tag, obrigatorio=True):
    padrao = rf"<{tag}>([^<\r\n]+)"

    resultado = re.search(
        padrao,
        texto,
        flags=re.IGNORECASE,
    )

    if resultado:
        return resultado.group(1).strip()

    if obrigatorio:
        raise ValueError(
            f"Tag obrigatoria ausente: {tag}"
        )

    return ""


def _cabecalho(texto, nome):
    resultado = re.search(
        rf"(?im)^{re.escape(nome)}:(.+)$",
        texto,
    )

    if not resultado:
        return ""

    return resultado.group(1).strip()


def _parse_data_ofx(valor):
    # Exemplo:
    # 20260701120000[-3:BRT]

    principal = valor[:14]

    dt = datetime.strptime(
        principal,
        "%Y%m%d%H%M%S",
    )

    fuso = re.search(
        r"\[([+-]?\d+):",
        valor,
    )

    if not fuso:
        return dt

    deslocamento = int(
        fuso.group(1)
    )

    return dt.replace(
        tzinfo=timezone(
            timedelta(hours=deslocamento)
        )
    )


def _detectar_encoding(dados):
    cabecalho = dados[:1000].decode(
        "ascii",
        errors="ignore",
    )

    charset = _cabecalho(
        cabecalho,
        "CHARSET",
    )

    if charset == "1252":
        return "cp1252"

    if charset.upper() in {
        "UTF-8",
        "UTF8",
    }:
        return "utf-8"

    return "latin-1"


def parse_ofx_bytes(dados):
    encoding = _detectar_encoding(
        dados
    )

    texto = dados.decode(
        encoding,
        errors="strict",
    )

    versao = _cabecalho(
        texto,
        "VERSION",
    )

    charset = _cabecalho(
        texto,
        "CHARSET",
    )

    blocos = re.findall(
        r"<STMTTRN>(.*?)</STMTTRN>",
        texto,
        flags=(
            re.IGNORECASE
            | re.DOTALL
        ),
    )

    movimentos = []

    for bloco in blocos:
        movimento = MovimentoOFX(
            tipo=_valor_tag(
                bloco,
                "TRNTYPE",
            ),
            data_postagem=_parse_data_ofx(
                _valor_tag(
                    bloco,
                    "DTPOSTED",
                )
            ),
            valor=Decimal(
                _valor_tag(
                    bloco,
                    "TRNAMT",
                )
            ),
            fitid=_valor_tag(
                bloco,
                "FITID",
                obrigatorio=False,
            ),
            checknum=_valor_tag(
                bloco,
                "CHECKNUM",
                obrigatorio=False,
            ),
            memo=_valor_tag(
                bloco,
                "MEMO",
                obrigatorio=False,
            ),
        )

        movimentos.append(
            movimento
        )

    return ExtratoOFX(
        versao=versao,
        charset=charset,
        moeda=_valor_tag(
            texto,
            "CURDEF",
        ),
        banco=_valor_tag(
            texto,
            "BANKID",
        ),
        conta=_valor_tag(
            texto,
            "ACCTID",
        ),
        tipo_conta=_valor_tag(
            texto,
            "ACCTTYPE",
        ),
        data_inicio=_valor_tag(
            texto,
            "DTSTART",
        ),
        data_fim=_valor_tag(
            texto,
            "DTEND",
        ),
        saldo=Decimal(
            _valor_tag(
                texto,
                "BALAMT",
            )
        ),
        data_saldo=_valor_tag(
            texto,
            "DTASOF",
        ),
        movimentos=tuple(
            movimentos
        ),
    )


def parse_ofx(caminho):
    caminho = Path(caminho)

    return parse_ofx_bytes(
        caminho.read_bytes()
    )
