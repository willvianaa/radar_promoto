"""Migrações: o que dá para validar sem Postgres.

Sem Postgres local, o SQL real (schemas, jsonb, plpgsql) NÃO foi executado aqui. O que se garante:
a cópia do DDL é idêntica ao contrato, o parâmetro nº 1 é idêntico ao do modelo.md, a cadeia de
revisões é linear e o modo offline do Alembic emite o DDL e o INSERT esperados.
"""

import io
import json
import re
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from regras.parametros import PARAMETROS_V1

RAIZ = Path(__file__).resolve().parent.parent


def _cfg(buf=None) -> Config:
    cfg = Config(str(RAIZ / "db" / "alembic.ini"), output_buffer=buf) if buf else Config(str(RAIZ / "db" / "alembic.ini"))
    cfg.set_main_option("script_location", str(RAIZ / "db" / "migrations"))
    return cfg


def test_ddl_da_migracao_e_o_contrato():
    assert (RAIZ / "db" / "migrations" / "sql" / "0001_modelo.sql").read_bytes() == (RAIZ / "db" / "modelo.sql").read_bytes()


def test_parametro_v1_igual_ao_modelo_md():
    md = (RAIZ / "db" / "modelo.md").read_text(encoding="utf-8")
    bloco = re.search(r"```json\n(.*?)\n```", md, re.S).group(1)
    assert json.loads(bloco) == PARAMETROS_V1


def test_cadeia_linear_de_revisoes():
    sd = ScriptDirectory.from_config(_cfg())
    assert [r.revision for r in sd.walk_revisions()] == ["0002", "0001"]
    assert sd.get_heads() == ["0002"]


def test_offline_emite_ddl_e_parametro():
    buf = io.StringIO()
    command.upgrade(_cfg(buf), "base:head", sql=True)
    sql = buf.getvalue()
    contrato = (RAIZ / "db" / "modelo.sql").read_text(encoding="utf-8")
    assert contrato.strip() in sql
    assert "INSERT INTO app.parametro_versao" in sql
    assert '"meta2": 93' in sql
    assert "setval(pg_get_serial_sequence('app.parametro_versao'" in sql


def test_offline_downgrade_remove_esquemas():
    buf = io.StringIO()
    command.downgrade(_cfg(buf), "0002:base", sql=True)
    sql = buf.getvalue()
    for esquema in ("app", "core", "raw"):
        assert f"DROP SCHEMA IF EXISTS {esquema} CASCADE" in sql
