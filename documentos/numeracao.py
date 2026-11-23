"""Numeração RP-AAAA-NNNNNN, sequencial por ano (db/modelo.md, app.dossie_sequencia).

O número sai de um UPSERT que incrementa a linha do ano. Em Postgres, isso
trava a linha até o COMMIT: emissões concorrentes do mesmo ano esperam uma
pela outra, e nenhuma recebe o mesmo número. Como o incremento faz parte da
mesma transação que grava o dossiê, um ROLLBACK também desfaz o incremento,
e não sobra buraco na sequência.

Chamar sempre dentro da transação que grava app.dossie com o número.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import text

FUSO = ZoneInfo("America/Sao_Paulo")
NUMERO_RE = re.compile(r"^RP-\d{4}-\d{6}$")
TABELA_PADRAO = "app.dossie_sequencia"
_TABELA_VALIDA = re.compile(r"^[a-z_]+(\.[a-z_]+)?$")

_SQL = (
    "INSERT INTO {tabela} (ano, ultimo) VALUES (:ano, 1) "
    "ON CONFLICT (ano) DO UPDATE SET ultimo = {tabela}.ultimo + 1 "
    "RETURNING ultimo"
)


def formatar_numero(ano: int, sequencia: int) -> str:
    if not 1 <= sequencia <= 999_999:
        raise ValueError("sequência fora do intervalo de 6 dígitos")
    return f"RP-{ano:04d}-{sequencia:06d}"


def ano_de_emissao(emitido_em: datetime) -> int:
    """Ano civil no fuso da operação (America/Sao_Paulo)."""
    if emitido_em.tzinfo is None:
        raise ValueError("emitido_em precisa ter fuso")
    return emitido_em.astimezone(FUSO).year


def proximo_numero(conexao: Any, ano: int, tabela: str = TABELA_PADRAO) -> str:
    """Reserva o próximo número do ano dentro da transação de `conexao`.

    `conexao` é uma Connection do SQLAlchemy já com transação aberta.
    """
    if not _TABELA_VALIDA.match(tabela):
        raise ValueError("nome de tabela inválido")
    sequencia = conexao.execute(text(_SQL.format(tabela=tabela)), {"ano": ano}).scalar_one()
    return formatar_numero(ano, int(sequencia))
