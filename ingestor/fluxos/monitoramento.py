"""Plataforma de monitoramento: cadastro, operação, atividades, humor e fotos.

Seletores concentrados aqui para a homologação ajustar sem tocar na lógica. Só consulta e exporta.
Fotos: baixa o ZIP do lote para o storage raw; o manifesto e a gravação ficam para o PR de fotos.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from ingestor.fluxos.comum import Credenciais, checar_bloqueio, login

# origem -> (caminho do relatório, extensão do arquivo exportado, dias por fatia)
RELATORIOS = {
    "colaboradores": ("/cadastro/colaboradores", "csv", None),  # carga completa diária
    "operacao": ("/relatorios/checkin", "xlsx", 1),
    "atividades": ("/relatorios/pesquisas", "csv", 1),
    "humor": ("/relatorios/humor", "xlsx", 14),
    "fotos": ("/relatorios/fotos", "zip", 1),
}


def baixar_relatorio(page, cred: Credenciais, origem: str, ini: dt.date, fim: dt.date, destino: Path) -> Path:
    """Abre o relatório, aplica o período e clica em Exportar. Retorna o arquivo salvo em `destino`."""
    caminho, ext, _ = RELATORIOS[origem]
    page.goto(cred.url + caminho)
    checar_bloqueio(page)
    if RELATORIOS[origem][2] is not None:
        page.fill('input[name="data_ini"]', ini.isoformat())
        page.fill('input[name="data_fim"]', fim.isoformat())
    with page.expect_download() as info:
        page.get_by_role("button", name="Exportar").click()
    nome = f"{origem}_{ini:%Y%m%d}_{fim:%Y%m%d}.{ext}"
    saida = destino / nome
    info.value.save_as(saida)
    return saida


class SessaoMonitoramento:
    """Contexto: abre o navegador, faz login e expõe `baixar(origem, ini, fim)`."""

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

    def baixar(self, origem: str, ini: dt.date, fim: dt.date) -> list[tuple[Path, dict | None]]:
        return [(baixar_relatorio(self.page, self.cred, origem, ini, fim, self.destino), None)]
