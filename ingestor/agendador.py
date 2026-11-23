"""Agendador do worker: executa o ingestor todo dia às 05:00 (America/Sao_Paulo).

Equivale ao cron `0 5 * * *` no fuso de São Paulo. Por enquanto a execução é um
placeholder: registra que não há origem configurada e não lê nenhum dado.

Uso:
    python -m ingestor.agendador            # loop diário (container worker)
    python -m ingestor.agendador --uma-vez  # executa uma vez e sai (testes, manutenção)
"""

from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")
HORA_EXECUCAO = (5, 0)  # 05:00

log = logging.getLogger("ingestor")


def proxima_execucao(agora: datetime) -> datetime:
    """Próximo instante 05:00 (America/Sao_Paulo) estritamente posterior a `agora`."""
    local = agora.astimezone(FUSO)
    hora, minuto = HORA_EXECUCAO
    candidato = local.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    if candidato <= local:
        candidato += timedelta(days=1)
    return candidato


def executar_ingestor() -> None:
    """Placeholder: a carga real (Playwright, raw.carga, validação por schemas/) é da Onda 2."""
    log.info("ingestor: execução placeholder; nenhuma origem configurada, nada foi lido")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agendador do ingestor do Radar Promotor")
    parser.add_argument("--uma-vez", action="store_true", help="executa uma vez e sai")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    if args.uma_vez:
        executar_ingestor()
        return 0

    while True:
        agora = datetime.now(FUSO)
        alvo = proxima_execucao(agora)
        log.info("próxima execução do ingestor: %s", alvo.isoformat())
        time.sleep(max(0.0, (alvo - datetime.now(FUSO)).total_seconds()))
        executar_ingestor()


if __name__ == "__main__":
    raise SystemExit(main())
