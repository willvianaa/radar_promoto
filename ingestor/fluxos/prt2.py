"""2PRT: Tabela Analítica (Todos e DESCONTOS) e PDOH (4 rankings XLSX).

Limites duros (CLAUDE.md / harness): só filtros e "Exportar XLSX". NUNCA "Atualizar Aderência" nem
"Gerar Aderência"; se aparecer o diálogo "Recalcular", clicar Cancelar; ao terminar, filtros voltam ao padrão.
Todo clique passa por `_clicar`, que recusa os rótulos proibidos.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from ingestor.fluxos.comum import Credenciais, checar_bloqueio, login, meses

PROIBIDOS = ("atualizar aderencia", "gerar aderencia")
GRUPOS = ("Todos", "DESCONTOS")
RANKINGS = {"prod": "Produtividade", "desl": "Deslocamento", "ocio": "Ócio", "hnr": "Horas não Registradas"}
ARQUIVO_PDOH = {"prod": "ranking_pdoh_prod", "desl": "ranking_pdoh_desl", "ocio": "ranking_pdoh_ocio", "hnr": "ranking_pdoh_hnr"}


class AcaoProibida(Exception):
    pass


def _norm(t: str) -> str:
    import unicodedata

    s = unicodedata.normalize("NFKD", t or "")
    return " ".join("".join(c for c in s if not unicodedata.combining(c)).lower().split())


def _clicar(locator) -> None:
    rotulo = _norm(locator.inner_text() or locator.get_attribute("value") or locator.get_attribute("aria-label") or "")
    if any(p in rotulo for p in PROIBIDOS):
        raise AcaoProibida("clique recusado: ação que altera dados na origem")
    locator.click()


def _cancelar_recalcular(page) -> None:
    dlg = page.locator('[role="dialog"]:has-text("Recalcular")')
    if dlg.count():
        dlg.get_by_role("button", name="Cancelar").click()


def _exportar(page, locator, destino: Path, nome: str) -> Path:
    with page.expect_download() as info:
        _clicar(locator)
    saida = destino / nome
    info.value.save_as(saida)
    _cancelar_recalcular(page)
    return saida


def baixar_aderencia(page, cred: Credenciais, ini: dt.date, fim: dt.date, destino: Path) -> list[tuple[Path, dict | None]]:
    """Um XLSX por mês × grupo (Todos, DESCONTOS). Filtros voltam ao padrão no fim."""
    arquivos = []
    page.goto(cred.url + "/aderencia")
    checar_bloqueio(page)
    padrao = {n: page.locator(f'select[name="{n}"]').input_value() for n in ("grupo", "mes", "ano")}
    for m_ini, _ in meses(ini, fim):
        for grupo in GRUPOS:
            page.select_option('select[name="ano"]', str(m_ini.year))
            page.select_option('select[name="mes"]', str(m_ini.month))
            page.select_option('select[name="grupo"]', grupo)
            nome = f"aderencia_{m_ini:%Y%m}_{grupo.lower()}.xlsx"
            arquivos.append((_exportar(page, page.get_by_role("button", name="Exportar XLSX"), destino, nome), None))
    for n, v in padrao.items():
        page.select_option(f'select[name="{n}"]', v)
    return arquivos


def baixar_pdoh(page, cred: Credenciais, ini: dt.date, fim: dt.date, destino: Path) -> list[tuple[Path, dict | None]]:
    """Aba Rankings: um XLSX por ranking (a aba Detalhada corta em 5.000 linhas e não é usada)."""
    page.goto(cred.url + "/pdoh")
    checar_bloqueio(page)
    page.get_by_role("tab", name="Rankings").click()
    padrao = {n: page.locator(f'input[name="{n}"]').input_value() for n in ("data_ini", "data_fim")}
    page.fill('input[name="data_ini"]', ini.isoformat())
    page.fill('input[name="data_fim"]', fim.isoformat())
    arquivos = []
    for cat in RANKINGS:
        botao = page.locator(f'[data-ranking="{cat}"]').get_by_role("button", name="XLSX")
        extras = {"categoria": cat, "periodo_ini": ini.isoformat(), "periodo_fim": fim.isoformat()}
        arquivos.append((_exportar(page, botao, destino, f"{ARQUIVO_PDOH[cat]}_{ini:%Y%m%d}_{fim:%Y%m%d}.xlsx"), extras))
    for n, v in padrao.items():
        page.fill(f'input[name="{n}"]', v)
    return arquivos


class Sessao2PRT:
    def __init__(self, playwright, cred: Credenciais, destino: Path):
        self.cred, self.destino = cred, destino
        self.browser = playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(accept_downloads=True)
        self.page = self.context.new_page()

    def __enter__(self):
        login(self.page, self.cred)
        return self

    def __exit__(self, *a):
        self.browser.close()

    def baixar(self, origem: str, ini: dt.date, fim: dt.date):
        fn = {"aderencia": baixar_aderencia, "pdoh": baixar_pdoh}[origem]
        return fn(self.page, self.cred, ini, fim, self.destino)
