"""Utilitários: nomes, CPF, datas, horas e distância."""

from __future__ import annotations

import math
import re
import unicodedata
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache


_ESPACOS = re.compile(r"\s+")


def norm_nome(s) -> str:
    """Maiúsculas, sem acento, espaços simples (CLAUDE.md §3)."""
    if s is None:
        return ""
    return _norm_str(s if isinstance(s, str) else str(s))


@lru_cache(maxsize=200_000)
def _norm_str(s: str) -> str:
    # memoizado: nomes de loja, humor e colaborador se repetem milhões de vezes no cálculo em volume
    t = unicodedata.normalize("NFD", s)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return _ESPACOS.sub(" ", t.upper()).strip()


def normaliza_cpf(v) -> str:
    """Só dígitos. Número vindo de planilha perde zeros à esquerda: completa para 11. Inválido → ''."""
    if v is None or v == "":
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    d = re.sub(r"\D", "", str(v))
    if isinstance(v, int) and 0 < len(d) < 11:
        d = d.zfill(11)
    return d if len(d) == 11 else ""


def mascara_cpf(cpf: str) -> str:
    """***.456.789-** (listas, rankings e exports agregados). Chave provisória não é mascarável."""
    d = re.sub(r"\D", "", cpf or "")
    return f"***.{d[3:6]}.{d[6:9]}-**" if len(d) == 11 else ""


def parse_data(v) -> date | None:
    """ISO, dd/mm/aaaa, datetime/date e serial do Excel."""
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, (int, float)):
        if v < 20000:
            return None
        return (datetime(1899, 12, 30) + timedelta(days=int(v))).date()
    s = str(v).strip()
    m = re.match(r"^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})", s)
    if m:
        a = int(m.group(3))
        a += 2000 if a < 100 else 0
        return date(a, int(m.group(2)), int(m.group(1)))
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", s)
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def parse_hora(v) -> int | None:
    """Minutos desde 00:00 a partir de hh:mm, datetime/time ou fração de dia do Excel."""
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.hour * 60 + v.minute
    if hasattr(v, "hour") and hasattr(v, "minute"):
        return v.hour * 60 + v.minute
    if isinstance(v, (int, float)):
        return round((v - math.floor(v)) * 1440)
    m = re.search(r"(\d{1,2}):(\d{2})", str(v))
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def parse_num(v) -> float | None:
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[%\s]", "", str(v))
    s = re.sub(r"\.(?=\d{3}(\D|$))", "", s).replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def segunda_da_semana(d: date) -> date:
    return d - timedelta(days=d.weekday())


def semana_iso(d: date) -> int:
    return d.isocalendar()[1]


def segunda_da_semana_iso(ano: int, semana: int) -> date:
    return date.fromisocalendar(ano, semana, 1)


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p = math.pi / 180
    a = math.sin((lat2 - lat1) * p / 2) ** 2 + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def arredonda(x: float) -> int:
    """Math.round do JavaScript (meio para cima), não o arredondamento do banqueiro do Python."""
    return math.floor(x + 0.5)


def fmt_pct(x: float | None, casas: int = 1) -> str:
    """Percentual pt-BR com meio para cima (igual ao toFixed do protótipo, não ao arredondamento do banqueiro)."""
    if x is None:
        return "—"
    q = Decimal(x * 100).quantize(Decimal(1).scaleb(-casas), rounding=ROUND_HALF_UP)
    return f"{q:.{casas}f}".replace(".", ",") + "%"


def plural(n: int, singular: str, plural_: str) -> str:
    return f"{n} {singular if n == 1 else plural_}"
