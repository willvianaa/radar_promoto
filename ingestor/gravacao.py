"""Gravação em raw: `raw.carga` (SHA-256, período, "Gerado em") + `raw.linha` (JSONB).

Formato alterado grava NADA em raw e abre `app.ingestao_alerta`. Mesmo arquivo (origem + SHA-256) não
é regravado. `conn` é uma conexão psycopg 3; a transação é aberta aqui (`conn.transaction()`).
O alerta registra só o motivo (nomes de colunas, contagens), nunca valores de células.
"""

from __future__ import annotations

import datetime as dt
import logging
from dataclasses import dataclass
from pathlib import Path

from psycopg.types.json import Jsonb

from ingestor.validacao import FORMATO_ALTERADO, OK, Resultado

log = logging.getLogger("ingestor.gravacao")


@dataclass
class Gravado:
    status: str  # 'gravado' | 'duplicado' | 'formato_alterado'
    carga_id: int | None = None
    motivo: str | None = None


def gravar(
    conn,
    res: Resultado,
    arquivo: Path | str,
    *,
    periodo_ini: dt.date | None = None,
    periodo_fim: dt.date | None = None,
    gerado_em_origem: dt.datetime | None = None,
) -> Gravado:
    nome = Path(arquivo).name
    if res.status not in (OK, FORMATO_ALTERADO):
        raise ValueError(f"status inesperado: {res.status}")
    with conn.transaction():
        if res.status == FORMATO_ALTERADO:
            conn.execute(
                "INSERT INTO app.ingestao_alerta (origem, motivo) VALUES (%s, %s)", (res.origem, res.motivo)
            )
            log.warning("ingestor: formato alterado na origem %s: %s", res.origem, res.motivo)
            return Gravado("formato_alterado", motivo=res.motivo)

        ja = conn.execute(
            "SELECT id FROM raw.carga WHERE origem = %s AND sha256 = %s", (res.origem, res.sha256)
        ).fetchone()
        if ja:
            return Gravado("duplicado", carga_id=ja[0])

        carga_id = conn.execute(
            "INSERT INTO raw.carga (origem, arquivo, sha256, periodo_ini, periodo_fim, gerado_em_origem,"
            " linhas_lidas, linhas_aceitas, linhas_descartadas, status, terminada_em)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'ok', now()) RETURNING id",
            (res.origem, nome, res.sha256, periodo_ini, periodo_fim, gerado_em_origem,
             res.linhas_lidas, res.linhas_aceitas, res.linhas_descartadas),
        ).fetchone()[0]
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO raw.linha (carga_id, n, dados) VALUES (%s, %s, %s)",
                [(carga_id, n, Jsonb(d)) for n, d in enumerate(res.linhas, start=1)],
            )
        return Gravado("gravado", carga_id=carga_id)
