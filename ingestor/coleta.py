"""Orquestra a coleta: baixa por fatia, valida, grava em raw. `executar()` é o ponto de entrada do agendador.

Fatiamento: cada fatia é baixada, validada e gravada; se o export vier no limite de 10 mil linhas
(possível truncamento), a janela é dividida ao meio e refeita, até 1 dia. Se mesmo 1 dia estoura,
abre alerta (nada é gravado).
"""

from __future__ import annotations

import datetime as dt
import logging
import os
from collections.abc import Callable
from pathlib import Path
from zoneinfo import ZoneInfo

from ingestor.fluxos.comum import (
    BloqueioOrigem,
    Credenciais,
    CredenciaisAusentes,
    ErroLogin,
    fatiar_periodo,
    pasta_raw,
)
from ingestor.gravacao import alertar, gravar
from ingestor.validacao import validar_arquivo

log = logging.getLogger("ingestor.coleta")
FUSO = ZoneInfo("America/Sao_Paulo")

Baixar = Callable[[dt.date, dt.date], list[tuple[Path, dict | None]]]


def coletar_janela(conn, origem: str, baixar: Baixar, ini: dt.date, fim: dt.date) -> list[str]:
    """Baixa [ini, fim], valida e grava. Retorna os status ('gravado', 'duplicado', 'formato_alterado')."""
    status: list[str] = []
    arquivos = baixar(ini, fim)
    res = [(arq, validar_arquivo(arq, origem, extras)) for arq, extras in arquivos]
    if any(r.excedeu_limite for _, r in res) and ini < fim:
        meio = ini + (fim - ini) // 2
        log.info("ingestor: %s no limite de linhas; dividindo a janela", origem)
        return coletar_janela(conn, origem, baixar, ini, meio) + coletar_janela(
            conn, origem, baixar, meio + dt.timedelta(days=1), fim
        )
    for arq, r in res:
        g = gravar(conn, r, arq, periodo_ini=ini, periodo_fim=fim)
        status.append(g.status)
    return status


def coletar_origem(conn, origem: str, baixar: Baixar, ini: dt.date, fim: dt.date, dias: int | None) -> list[str]:
    janelas = [(ini, fim)] if dias is None else fatiar_periodo(ini, fim, dias)
    out: list[str] = []
    for j_ini, j_fim in janelas:
        out += coletar_janela(conn, origem, baixar, j_ini, j_fim)
    return out


def _plano(hoje: dt.date) -> dict[str, list[tuple[str, dt.date, dt.date, int | None]]]:
    ontem = hoje - dt.timedelta(days=1)
    semana = hoje - dt.timedelta(days=7)
    mes_ant = (hoje.replace(day=1) - dt.timedelta(days=1)).replace(day=1)
    mes_atual = hoje.replace(day=1)
    return {
        "MONITORAMENTO": [
            ("colaboradores", ontem, ontem, None),
            ("operacao", semana, ontem, 1),
            ("atividades", semana, ontem, 1),
            ("humor", semana, ontem, 14),
        ],
        "2PRT": [
            ("aderencia", mes_ant, hoje, None),  # o fluxo já fatia por mês × grupo
            ("pdoh", mes_atual, ontem, None),
        ],
    }


def executar(env: dict[str, str] | None = None, hoje: dt.date | None = None) -> None:
    """Ponto de entrada do agendador (05:00). Origem sem credencial é pulada; bloqueio/login recusado
    para só aquela origem e abre alerta. Nunca contorna captcha/2FA."""
    import psycopg
    from playwright.sync_api import sync_playwright

    from ingestor.fluxos.monitoramento import SessaoMonitoramento
    from ingestor.fluxos.prt2 import Sessao2PRT

    env = dict(os.environ) if env is None else env
    hoje = hoje or dt.datetime.now(FUSO).date()
    url_banco = env.get("DATABASE_URL")
    if not url_banco:
        log.error("ingestor: DATABASE_URL ausente; nada foi coletado")
        return
    destino = pasta_raw(env)
    sessoes = {"MONITORAMENTO": SessaoMonitoramento, "2PRT": Sessao2PRT}
    with psycopg.connect(url_banco) as conn, sync_playwright() as pw:
        for nome, itens in _plano(hoje).items():
            try:
                cred = Credenciais.do_ambiente(nome, env)
            except CredenciaisAusentes:
                log.warning("ingestor: origem %s sem credenciais; pulada", nome)
                continue
            try:
                with sessoes[nome](pw, cred, destino) as sessao:
                    for origem, ini, fim, dias in itens:
                        coletar_origem(conn, origem, lambda i, f, o=origem: sessao.baixar(o, i, f), ini, fim, dias)
            except (BloqueioOrigem, ErroLogin) as e:
                alertar(conn, nome.lower(), str(e))
                log.warning("ingestor: origem %s interrompida: %s", nome, e)
            except Exception as e:  # falha inesperada numa origem não derruba as demais
                alertar(conn, nome.lower(), f"erro inesperado ({type(e).__name__})")
                log.exception("ingestor: erro inesperado em %s", nome)
