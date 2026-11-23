"""Contrato: o que a API implementa tem de existir em api/openapi.yaml, com o mesmo método."""

from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from api.app.main import app

from .fakes import SENHA

SPEC = yaml.safe_load((Path(__file__).resolve().parents[2] / "api" / "openapi.yaml").read_text(encoding="utf-8"))
BASE = SPEC["servers"][0]["url"]
METODOS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


def _implementadas():
    for r in app.routes:
        if getattr(r, "include_in_schema", False) and r.path.startswith(BASE) and not r.path.endswith("openapi.json"):
            for m in r.methods & METODOS:
                yield r.path[len(BASE):], m.lower()


def test_toda_rota_implementada_esta_no_openapi():
    faltando = [(p, m) for p, m in _implementadas() if m not in SPEC["paths"].get(p, {})]
    assert not faltando, f"rotas fora do contrato (abrir PR na mãe): {faltando}"


def test_status_do_login_estao_no_contrato(client):
    resp = SPEC["paths"]["/auth/login"]["post"]["responses"]
    ok = client.post(f"{BASE}/auth/login", json={"email": "rh@ficticio.example.com", "senha": SENHA})
    ruim = client.post(f"{BASE}/auth/login", json={"email": "rh@ficticio.example.com", "senha": "x"})
    assert str(ok.status_code) in resp and str(ruim.status_code) in resp


def test_resposta_de_login_segue_o_schema_usuario(client):
    schema = {**SPEC["components"]["schemas"]["Usuario"], "components": SPEC["components"]}
    corpo = client.post(f"{BASE}/auth/login", json={"email": "sup@ficticio.example.com", "senha": SENHA}).json()
    Draft202012Validator(schema).validate(corpo)


def test_erro_segue_o_schema_erro(client):
    schema = {**SPEC["components"]["schemas"]["Erro"], "components": SPEC["components"]}
    r = client.get(f"{BASE}/auth/eu")
    assert r.status_code == 401
    Draft202012Validator(schema).validate(r.json())
