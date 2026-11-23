"""Fluxos de download contra páginas HTML SIMULADAS (tests/fixtures/ingestor/paginas). Nada de origem real."""

import datetime as dt
import io
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
from openpyxl import Workbook
from playwright.sync_api import sync_playwright

from ingestor.fluxos import monitoramento, prt2
from ingestor.fluxos.comum import (
    BloqueioOrigem,
    Credenciais,
    CredenciaisAusentes,
    ErroLogin,
    fatiar_periodo,
    login,
    meses,
)

PAGINAS = Path(__file__).resolve().parent.parent / "fixtures" / "ingestor" / "paginas"
BASE = "http://origem-simulada.test"
SENHA = "senha-ficticia"


def _xlsx_bytes() -> bytes:
    wb = Workbook()
    wb.active.append(["NOME DO COLABORADOR", "DATA", "HUMOR"])
    wb.active.append(["ANA FICTICIA", "20/11/2026", "Feliz"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


class SiteFalso:
    """Serve as páginas simuladas e registra cada download pedido."""

    def __init__(self, login_pagina="login.html"):
        self.login_pagina, self.downloads = login_pagina, []

    def __call__(self, route):
        u = urlparse(route.request.url)
        p = u.path
        if p.startswith("/download/"):
            self.downloads.append((p, {k: v[0] for k, v in parse_qs(u.query).items()}))
            ext = "csv" if p.endswith(("colaboradores", "pesquisas")) else "xlsx"
            corpo = b"ID;X\n1;2\n" if ext == "csv" else _xlsx_bytes()
            return route.fulfill(
                body=corpo,
                headers={"Content-Disposition": f'attachment; filename="x.{ext}"', "Content-Type": "application/octet-stream"},
            )
        pagina = {"/login": self.login_pagina, "/painel": "painel.html", "/aderencia": "aderencia.html", "/pdoh": "pdoh.html"}.get(
            p, "relatorio.html"
        )
        route.fulfill(body=(PAGINAS / pagina).read_text(encoding="utf-8"), content_type="text/html; charset=utf-8")


@pytest.fixture
def navegador():
    with sync_playwright() as pw:
        yield pw


def _cred(senha=SENHA):
    return Credenciais(BASE, "usuario-ficticio", senha)


def _sessao(cls, pw, destino, site):
    s = cls(pw, _cred(), destino)
    s.context.route(BASE + "/**", site)
    return s


def test_credenciais_so_de_ambiente_e_sem_vazar_no_repr():
    env = {"INGESTOR_2PRT_URL": BASE + "/", "INGESTOR_2PRT_USUARIO": "u", "INGESTOR_2PRT_SENHA": "segredo-ficticio"}
    c = Credenciais.do_ambiente("2PRT", env)
    assert c.url == BASE and "segredo-ficticio" not in repr(c)
    with pytest.raises(CredenciaisAusentes) as e:
        Credenciais.do_ambiente("MONITORAMENTO", env)
    assert "INGESTOR_MONITORAMENTO_SENHA" in str(e.value)


def test_fatiamento():
    j = fatiar_periodo(dt.date(2026, 11, 1), dt.date(2026, 11, 30), 14)
    assert j == [(dt.date(2026, 11, 1), dt.date(2026, 11, 14)), (dt.date(2026, 11, 15), dt.date(2026, 11, 28)),
                 (dt.date(2026, 11, 29), dt.date(2026, 11, 30))]
    assert meses(dt.date(2026, 10, 15), dt.date(2026, 11, 22)) == [
        (dt.date(2026, 10, 15), dt.date(2026, 10, 31)), (dt.date(2026, 11, 1), dt.date(2026, 11, 22))]


def test_login_recusado(navegador):
    site = SiteFalso()
    s = _sessao(monitoramento.SessaoMonitoramento, navegador, Path("."), site)
    s.cred = _cred("errada")
    with pytest.raises(ErroLogin), s:
        pass


@pytest.mark.parametrize("pagina", ["login_captcha.html", "login_otp.html"])
def test_captcha_e_2fa_param_sem_contornar(navegador, pagina):
    site = SiteFalso(pagina)
    s = _sessao(monitoramento.SessaoMonitoramento, navegador, Path("."), site)
    with pytest.raises(BloqueioOrigem), s:
        pass
    assert site.downloads == []


def test_monitoramento_baixa_e_valida(navegador, tmp_path):
    from ingestor.validacao import validar_arquivo

    site = SiteFalso()
    with _sessao(monitoramento.SessaoMonitoramento, navegador, tmp_path, site) as s:
        [(arq, extras)] = s.baixar("humor", dt.date(2026, 11, 20), dt.date(2026, 11, 20))
        s.baixar("colaboradores", dt.date(2026, 11, 21), dt.date(2026, 11, 21))
    assert arq.name == "humor_20261120_20261120.xlsx" and extras is None
    assert validar_arquivo(arq, "humor").status == "ok"
    assert site.downloads[0] == ("/download/humor", {"ini": "2026-11-20", "fim": "2026-11-20"})


def test_2prt_aderencia_so_exporta_e_cancela_recalcular(navegador, tmp_path):
    site = SiteFalso()
    with _sessao(prt2.Sessao2PRT, navegador, tmp_path, site) as s:
        arquivos = s.baixar("aderencia", dt.date(2026, 11, 3), dt.date(2026, 11, 20))
        pedidos = [q for _, q in site.downloads]
        assert [q["grupo"] for q in pedidos] == ["Todos", "DESCONTOS"]
        assert {q["mes"] for q in pedidos} == {"11"}
        assert len(arquivos) == 2
        assert s.page.evaluate("window.__proibido") is None  # Atualizar/Gerar Aderência nunca clicados
        assert s.page.evaluate("window.__recalcular") == "cancelado"
        # filtros de volta ao padrão
        assert s.page.locator('select[name="mes"]').input_value() == "1"
        assert s.page.locator('select[name="grupo"]').input_value() == "Todos"


def test_2prt_pdoh_quatro_rankings_com_extras(navegador, tmp_path):
    site = SiteFalso()
    with _sessao(prt2.Sessao2PRT, navegador, tmp_path, site) as s:
        arquivos = s.baixar("pdoh", dt.date(2026, 11, 1), dt.date(2026, 11, 14))
        assert s.page.locator('input[name="data_fim"]').input_value() == "2026-11-30"  # padrão restaurado
    assert [e["categoria"] for _, e in arquivos] == ["prod", "desl", "ocio", "hnr"]
    assert {a.name for a, _ in arquivos} == {f"ranking_pdoh_{c}_20261101_20261114.xlsx" for c in ("prod", "desl", "ocio", "hnr")}
    assert all(q["ini"] == "2026-11-01" and q["fim"] == "2026-11-14" for _, q in site.downloads)


def test_clique_em_acao_proibida_e_recusado(navegador):
    site = SiteFalso()
    with navegador.chromium.launch() as b:
        ctx = b.new_context()
        ctx.route(BASE + "/**", site)
        page = ctx.new_page()
        page.goto(BASE + "/aderencia")
        for rotulo in ("Atualizar Aderência", "Gerar Aderência"):
            with pytest.raises(prt2.AcaoProibida):
                prt2._clicar(page.get_by_role("button", name=rotulo))
        assert page.evaluate("window.__proibido") is None


def test_login_ok_isolado(navegador):
    with navegador.chromium.launch() as b:
        ctx = b.new_context()
        ctx.route(BASE + "/**", SiteFalso())
        page = ctx.new_page()
        login(page, _cred())
        assert page.locator("#painel").count() == 1
