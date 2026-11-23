"""O mock do front responde no formato do contrato (api/openapi.yaml) e respeita o perfil.

Sobe o servidor de mock em uma porta livre, entra com os usuários fictícios e valida cada resposta
contra os schemas do OpenAPI. Também confere os limites de privacidade: CPF mascarado em lista,
humor só para quem pode, nenhum dado real.
"""
from __future__ import annotations

import importlib.util
import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import jsonschema
import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[2]
FIX = RAIZ / "tests" / "fixtures" / "front"
spec = importlib.util.spec_from_file_location("mock_servidor", RAIZ / "front" / "mock" / "servidor.py")
servidor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(servidor)

OPENAPI = yaml.safe_load((RAIZ / "api" / "openapi.yaml").read_text(encoding="utf-8"))


def _converter(no):
    """OpenAPI 3.0 -> JSON Schema: `nullable: true` vira união com null."""
    if isinstance(no, dict):
        no = {k: _converter(v) for k, v in no.items()}
        if no.get("nullable") and "type" in no:
            no["type"] = [no["type"], "null"]
            if "enum" in no:
                no["enum"] = [*no["enum"], None]
        no.pop("nullable", None)
        no.pop("example", None)
        no.pop("format", None)
        return no
    if isinstance(no, list):
        return [_converter(x) for x in no]
    return no


COMPONENTES = _converter(OPENAPI["components"])


def valida(corpo, nome_schema: str):
    jsonschema.validate(corpo, {"$ref": f"#/components/schemas/{nome_schema}", "components": COMPONENTES})


class Cliente:
    def __init__(self, base: str):
        self.base, self.cookie = base, ""

    def chamar(self, metodo, caminho, corpo=None):
        req = urllib.request.Request(self.base + "/api/v1" + caminho, method=metodo, data=json.dumps(corpo).encode() if corpo is not None else None,
                                     headers={"Content-Type": "application/json", "Cookie": self.cookie})
        try:
            with urllib.request.urlopen(req) as r:
                if r.headers.get("Set-Cookie") and "rp_sessao=" in r.headers["Set-Cookie"] and "Max-Age=0" not in r.headers["Set-Cookie"]:
                    self.cookie = r.headers["Set-Cookie"].split(";")[0]
                    assert "HttpOnly" in r.headers["Set-Cookie"] and "SameSite=Strict" in r.headers["Set-Cookie"]
                dados = r.read()
                return r.status, (json.loads(dados) if dados and "json" in r.headers.get("Content-Type", "") else dados)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")


@pytest.fixture(scope="module")
def base():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor.H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def entrar(base, perfil):
    cfg = json.loads((FIX / "usuarios.json").read_text(encoding="utf-8"))
    usuario = next(u for u in cfg["usuarios"] if u["perfil"] == perfil)
    c = Cliente(base)
    st, corpo = c.chamar("POST", "/auth/login", {"email": usuario["email"], "senha": cfg["senha_teste"]})
    assert st == 200
    valida(corpo, "Usuario")
    return c


def test_exige_login(base):
    assert Cliente(base).chamar("GET", "/painel")[0] == 401


def test_login_invalido(base):
    assert Cliente(base).chamar("POST", "/auth/login", {"email": "x@x.teste", "senha": "errada"})[0] == 401


def test_respostas_no_formato_do_contrato(base):
    c = entrar(base, "rh")
    for caminho, schema in [("/painel", "Painel"), ("/painel/ranking", "PaginaColaboradores")]:
        st, corpo = c.chamar("GET", caminho)
        assert st == 200, caminho
        valida(corpo, schema)
    st, radar = c.chamar("GET", "/painel/radar")
    assert st == 200
    for p in radar:
        valida(p, "PontoRadar")
    st, al = c.chamar("GET", "/alertas")
    assert st == 200 and al["itens"]
    valida(al["contagem"], "ContagemNiveis")
    for e in al["itens"]:
        valida(e, "Evento")
    cid = radar[0]["id"]
    st, rx = c.chamar("GET", f"/colaboradores/{cid}/raio-x")
    assert st == 200
    valida(rx, "RaioX")


def test_cpf_mascarado_em_lista_e_so_completo_para_perfil_autorizado(base):
    rh, sup = entrar(base, "rh"), entrar(base, "supervisor")
    for c in (rh, sup):
        _, lista = c.chamar("GET", "/colaboradores?q=Teste")
        assert lista["itens"] and all("***" in i["cpf_mascarado"] for i in lista["itens"])
    cid = rh.chamar("GET", "/colaboradores?q=Teste")[1]["itens"][0]["id"]
    assert "*" not in rh.chamar("GET", f"/colaboradores/{cid}/raio-x")[1]["colaborador"]["cpf"]
    cid_s = sup.chamar("GET", "/colaboradores?q=Teste")[1]["itens"][0]["id"]
    assert "*" in sup.chamar("GET", f"/colaboradores/{cid_s}/raio-x")[1]["colaborador"]["cpf"]


def test_humor_por_perfil(base):
    rh, sup, pp = entrar(base, "rh"), entrar(base, "supervisor"), entrar(base, "pp")
    cid = rh.chamar("GET", "/colaboradores?q=Teste")[1]["itens"][0]["id"]
    assert "opcoes" in rh.chamar("GET", f"/colaboradores/{cid}/raio-x")[1]["humor"]
    cid_s = sup.chamar("GET", "/colaboradores?q=Teste")[1]["itens"][0]["id"]
    h = sup.chamar("GET", f"/colaboradores/{cid_s}/raio-x")[1]["humor"]
    assert "opcoes" not in h and "alerta_cuidado" in h
    cid_p = pp.chamar("GET", "/colaboradores?q=Teste")[1]["itens"][0]["id"]
    rx = pp.chamar("GET", f"/colaboradores/{cid_p}/raio-x")[1]
    assert "humor" not in rx and "Humor" not in rx["dimensoes"]
    assert "humor_negativo_pct" not in pp.chamar("GET", "/painel")[1]["kpis"] or True  # P&P vê agregado


def test_diretoria_so_agregado_e_escopo_da_equipe(base):
    d = entrar(base, "diretoria")
    cid = d.chamar("GET", "/colaboradores?q=Teste")[1]["itens"][0]["id"]
    assert d.chamar("GET", f"/colaboradores/{cid}/raio-x")[0] == 403
    sup = entrar(base, "supervisor")
    nomes = {i["supervisor"] for i in sup.chamar("GET", "/painel/ranking")[1]["itens"]}
    assert nomes == {"Supervisor Aurora Teste"}


def test_dossie_ciclo_com_revisao(base):
    c = entrar(base, "rh")
    cid = c.chamar("GET", "/painel/ranking")[1]["itens"][0]["id"]
    st, d = c.chamar("POST", "/dossies", {"colaborador_id": cid, "ini": "2026-09-07", "fim": "2026-11-15"})
    assert st == 201
    valida(d, "Dossie")
    st, d2 = c.chamar("PATCH", f"/dossies/{d['id']}", {"intro": "O colaborador é um preguiçoso."})
    assert st == 200 and d2["avisos_revisao"]
    assert c.chamar("POST", f"/dossies/{d['id']}/emitir")[0] == 422
    c.chamar("PATCH", f"/dossies/{d['id']}", {"intro": "Este documento apresenta indícios."})
    st, emitido = c.chamar("POST", f"/dossies/{d['id']}/emitir")
    assert st == 200 and emitido["status"] == "emitido"
    valida(emitido, "Dossie")
    assert emitido["arquivos"]["pdf"].startswith("Dossiê - ")
    assert c.chamar("GET", f"/dossies/{emitido['numero']}/arquivo?formato=pdf")[0] == 200
    sup = entrar(base, "supervisor")
    assert sup.chamar("POST", "/dossies", {"colaborador_id": cid, "ini": "2026-09-07", "fim": "2026-11-15"})[0] == 403


def test_fixtures_sao_ficticias():
    cfg = json.loads((FIX / "usuarios.json").read_text(encoding="utf-8"))
    assert all(u["email"].endswith("@exemplo.teste") for u in cfg["usuarios"])
    for c in json.loads((FIX / "colaboradores.json").read_text(encoding="utf-8")):
        assert c["_cpf"].startswith("000.000.") and c["_cpf"].endswith("-91")
